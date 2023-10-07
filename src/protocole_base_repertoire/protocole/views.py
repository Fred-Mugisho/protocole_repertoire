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
        messages = MessageSimulation.objects.all()
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
    
def reinitialisation_data(request):
    try:
        Node.objects.all().delete()
        Node.objects.create(name='Local', numero=0)
        Node.objects.create(name='Home', numero=1)
        Node.objects.create(name='Remote', numero=2)

        MemoryBloc.objects.all().delete()
        block_0 = MemoryBloc(block_num=0, data='D0')
        block_1 = MemoryBloc(block_num=1, data='D1')
        block_2 = MemoryBloc(block_num=2, data='D2')
        block_3 = MemoryBloc(block_num=3, data='D3')

        block_0.save()
        block_1.save()
        block_2.save()
        block_3.save()

        Directory.objects.all().delete()
        Directory.objects.create(bloc=block_0, state='1', owner_bits='---')
        Directory.objects.create(bloc=block_1, state='1', owner_bits='---')
        Directory.objects.create(bloc=block_2, state='1', owner_bits='---')
        Directory.objects.create(bloc=block_3, state='1', owner_bits='---')

        return redirect('protocole:simulation')

    except Exception as e:
        return HttpResponse(f"<h2>Error page ==> {e}</h2>")

