from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *

def index(request):
    try:
        return render(request, 'protocole/index.html')
    except Exception as e:
        return HttpResponse(f"<h2>Error page ==> {e}</h2>")
    
def simulation(request):
    try:
        nodes = Node.objects.all()
        directory = Directory.objects.all()
        messages = MessageSimulation.objects.all().order_by('-id')
        blocks = MemoryBloc.objects.all()

        context = {
            'nodes': nodes,
            'directory': directory,
            'messages': messages,
            'blocks': blocks,
        }
        return render(request, 'protocole/simulation.html', context)
    except Exception as e:
        return HttpResponse(f"<h2>Error page ==> {e}</h2>")

# Generateur de message
def message_sender(type_message: str, source: str, dest: str, content_msg: str):
    MessageSimulation.objects.create(
        type_message=type_message,
        source=source,
        destination=dest,
        content_msg=content_msg,
    )

# Generateur de charer bits
def owner_bits(bits_list: list):
    if len(bits_list) >= 3:
        return '111'
    elif len(bits_list) == 2:
        if ['Local', 'Home'] == bits_list:
            return '110'
        if ['Local', 'Remote'] == bits_list:
            return '101'
        else:
            return '011'
    elif len(bits_list) == 1:
        if 'Local' in bits_list:
            return '100'
        if 'Home' in bits_list:
            return '010'
        else:
            return '001'
    else:
        return '000'

def read_data(request):
    try:
        if request.method == 'POST':
            node_id = int(request.POST.get('node'))
            block_id = int(request.POST.get('block'))

            node = Node.objects.get(id=node_id)
            block = Directory.objects.get(id=block_id)

            if block.state != '3':
                caches_node = CacheNode.objects.filter(node=node).filter(bloc=block.bloc)
                if caches_node.exists():
                    cache_node = caches_node.latest('id')
                    if cache_node.state_cache != '2': # 2: Shared
                        cache_node.state_cache = '2' # 2: Shared
                        cache_node.save()
                else:
                    CacheNode.objects.create(
                        node=node,
                        bloc=block.bloc,
                        state_cache='2',
                    )

                    node_home = Node.objects.get(numero=0)
                    MessageSimulation.objects.all().delete()
                    message_sender(
                        'Read Miss',
                        f"Cache {node.name}",
                        f"Repertoire {node_home.name}",
                        f"{node.node_string}, {block.string_block}",
                    )
                    message_sender(
                        'Data Value Reply',
                        f"Repertoire {node_home.name}",
                        f"Cache {node.name}",
                        content_msg=f"{block.bloc.data}",
                    )
            else:
                caches_all = CacheNode.objects.filter(state_cache='3') # 3: Modified
                cache_owner = None
                if caches_all.exists():
                    cache_owner = caches_all.latest('id')

                caches_node = CacheNode.objects.filter(node=node).filter(bloc=block.bloc)
                if caches_node.exists():
                    cache_node = caches_node.latest('id')
                    if cache_node.state_cache != '2': # 2: Shared
                        cache_node.state_cache = '2' # 2: Shared
                        cache_node.save()

                    node_home = Node.objects.get(numero=0)
                    if cache_owner is not None:
                        MessageSimulation.objects.all().delete()
                        message_sender(
                            'Fetch',
                            f"Repertoire {node_home.name}",
                            f"Cache {cache_owner.node.name}",
                            f"{block.string_block}",
                        )
                        message_sender(
                            'Data Write-Back',
                            f"Cache {cache_owner.node.name}",
                            f"Repertoire {node_home.name}",
                            f"{block.string_block}",
                        )
                        message_sender(
                            'Data Value Reply',
                            f"Repertoire {node_home.name}",
                            f"Cache {node.name}",
                            f"{block.string_block}",
                        )

                else:
                    CacheNode.objects.create(
                        node=node,
                        bloc=block.bloc,
                        state_cache='2', # 2: Shared
                    )

                    node_home = Node.objects.get(numero=0)
                    if cache_owner is not None:
                        MessageSimulation.objects.all().delete()
                        message_sender(
                            'Fetch',
                            f"Repertoire {node_home.name}",
                            f"Cache {cache_owner.node.name}",
                            f"{block.string_block}",
                        )
                        message_sender(
                            'Data Write-Back',
                            f"Cache {cache_owner.node.name}",
                            f"Repertoire {node_home.name}",
                            f"{block.string_block}",
                        )
                        message_sender(
                            'Data Value Reply',
                            f"Repertoire {node_home.name}",
                            f"Cache {node.name}",
                            f"{block.string_block}",
                        )
            
            caches = CacheNode.objects.filter(bloc=block.bloc)
            bits_list = []
            if caches.exists():
                for c in caches:
                    bits_list.append(c.node.name)

                block.state = '2' # 2: Shared
                block.owner_bits = owner_bits(bits_list)
                block.save()

            
            return redirect('protocole:simulation')
    except Exception as e:
        return HttpResponse(f"<h2>Error page ==> {e}</h2>")
    
def write_data(request):
    try:
        if request.method == 'POST':
            node_id = int(request.POST.get('node'))
            block_id = int(request.POST.get('block'))
            data = str(request.POST.get('data_send'))

            if data != '':
                node = Node.objects.get(id=node_id)
                block = Directory.objects.get(id=block_id)

                block_memory = MemoryBloc.objects.get(id=block.bloc.id)
                block_memory.data = data
                block_memory.save()

                node_home = Node.objects.get(numero=0)

                if block.state == '1': # 1: Uncached
                    MessageSimulation.objects.all().delete()
                    message_sender(
                        'Write Miss',
                        f"Cache {node.name}",
                        f"Repertoire {node_home.name}",
                        f"{node.node_string}, {block.string_block}",
                    )
                    message_sender(
                        'Data Value Reply',
                        f"Repertoire {node_home.name}",
                        f"Cache {node.name}",
                        f"{block.string_block}",
                    )
                    CacheNode.objects.create(
                        node=node,
                        bloc=block.bloc,
                        state_cache='3', # 3: Modified
                    )
                    if node.name == 'Home':
                        bit_shared = '100'
                    elif node.name == 'Local':
                        bit_shared = '010'
                    elif node.name == 'Remote':
                        bit_shared = '001'
                    
                    block.state = '3' # 3: Modified
                    block.owner_bits = bit_shared
                    block.save()

                elif block.state == '2': # 2: Shared
                    MessageSimulation.objects.all().delete()
                    message_sender(
                        'Data Value Reply',
                        f"Repertoire {node_home.name}",
                        f"Cache {node.name}",
                        f"{block.bloc.data}",
                    )

                    block_in_chached = CacheNode.objects.filter(bloc=block_memory)
                    if block_in_chached.exists():
                        for block_cache in block_in_chached:
                            message_sender(
                                'Invalidate',
                                f"Repertoire {node_home.name}",
                                f"Cache {block_cache.node.name}",
                                f"{block.string_block}",
                            )
                            block_cache.state_cache = '4' # 4: Invalid
                            block_cache.save()
                    
                    proprio = block_in_chached.filter(node=node)
                    if proprio.exists():
                        cached = proprio.latest('id')
                        cached.state_cache = '3' # 3: Modified
                        cached.save()

                    else:
                        CacheNode.objects.create(
                            node=node,
                            bloc=block.bloc,
                            state_cache='3', # 3: Modified
                        )

                    if node.name == 'Home':
                        bit_shared = '100'
                    elif node.name == 'Local':
                        bit_shared = '010'
                    elif node.name == 'Remote':
                        bit_shared = '001'
                    block.state = '3'
                    block.owner_bits = bit_shared
                    block.save()

                elif block.state == '3': # 3: Modified
                    MessageSimulation.objects.all().delete()
                    message_sender(
                        'Write Miss',
                        f"Cache {node.name}",
                        f"Repertoire {node_home.name}",
                        f"{node.node_string}, {block.string_block}",
                    )

                    cache_modified = CacheNode.objects.filter(bloc=block_memory).filter(state_cache='3')
                    if cache_modified.exists():
                        modif_cache = cache_modified.latest('id')
                        modif_cache.state_cache = '4'
                        modif_cache.save()

                    message_sender(
                        'Fetch/Invalidate',
                        f"Repertoire {node_home.name}",
                        f"Cache {node.name}",
                        f"{node.node_string}",
                    )
                    message_sender(
                        'Data Write-Back',
                        f"Cache {node.name}",
                        f"Repertoire {node_home.name}",
                        f"{node.node_string}, {block.string_block}",
                    )
                    message_sender(
                        'Data Value Reply',
                        f"Repertoire {node_home.name}",
                        f"Cache {node.name}",
                        f"{node.node_string}, {block.string_block}",
                    )
                    
                    proprio = CacheNode.objects.filter(bloc=block_memory).filter(node=node)
                    if proprio.exists():
                        cached = proprio.latest('id')
                        cached.state_cache = '3'
                        cached.save()

                    else:
                        CacheNode.objects.create(
                            node=node,
                            bloc=block.bloc,
                            state_cache='3',
                        )

                    if node.name == 'Home':
                        bit_shared = '100'
                    elif node.name == 'Local':
                        bit_shared = '010'
                    elif node.name == 'Remote':
                        bit_shared = '001'
                    block.state = '3'
                    block.owner_bits = bit_shared
                    block.save()


            return redirect('protocole:simulation')
        
    except Exception as e:
        return HttpResponse(f"<h2>Error page ==> {e}</h2>")
    
def reinitialisation_data(request):
    try:
        Directory.objects.all().delete()
        MessageSimulation.objects.all().delete()
        MemoryBloc.objects.all().delete()

        Node.objects.all().delete()
        Node.objects.create(name='Home', numero=0)
        Node.objects.create(name='Local', numero=1)
        Node.objects.create(name='Remote', numero=2)

        block_0 = MemoryBloc(block_num=0, data='D0')
        block_1 = MemoryBloc(block_num=1, data='D1')
        block_2 = MemoryBloc(block_num=2, data='D2')
        block_3 = MemoryBloc(block_num=3, data='D3')

        block_0.save()
        block_1.save()
        block_2.save()
        block_3.save()

        Directory.objects.create(bloc=block_0, state='1', owner_bits='---')
        Directory.objects.create(bloc=block_1, state='1', owner_bits='---')
        Directory.objects.create(bloc=block_2, state='1', owner_bits='---')
        Directory.objects.create(bloc=block_3, state='1', owner_bits='---')

        return redirect('protocole:simulation')

    except Exception as e:
        return HttpResponse(f"<h2>Error page ==> {e}</h2>")

