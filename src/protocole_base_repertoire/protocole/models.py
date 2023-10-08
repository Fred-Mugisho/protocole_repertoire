from django.db import models

# Create your models here.

node_choice = (
    ('Home', 'Home'),
    ('Local', 'Local'),
    ('Remote', 'Remote'),
)

state_block = (
    ('1', 'Uncached'),
    ('2', 'Shared'),
    ('3', 'Modified'),
    ('4', 'Invalid'),
)

msg_type_choice = (
    ('1', "Read Miss"),
    ('2', "Write Miss"),
    ('3', "Data Value Reply"),
    ('4', "Invalidate"),
    ('5', "Fetch"),
    ('6', "Fetch/Invalidate"),
    ('7', "Data Write-Back"),
)

class Node(models.Model):
    name = models.CharField(max_length=30, choices=node_choice, default='Home')
    numero = models.IntegerField()

    def __str__(self) -> str:
        return f"Node {self.numero} - {self.name}"
    
    @property
    def node_string(self):
        return f"Node {self.numero}"
    
    @property
    def all_caches(self):
        return CacheNode.objects.filter(node=self).order_by('-id')
    
class MemoryBloc(models.Model):
    block_num = models.IntegerField()
    data = models.CharField(max_length=20, default='--')

    def __str__(self) -> str:
        return f"B{self.block_num}"
    
    @property
    def string_block(self) -> str:
        return f"B{self.block_num}"
    
class Directory(models.Model):
    bloc = models.OneToOneField(MemoryBloc, on_delete=models.CASCADE)
    state = models.CharField(max_length=30, choices=state_block, default='1')
    owner_bits = models.CharField(max_length=5)

    def __str__(self) -> str:
        return self.bloc
    
    @property
    def string_block(self) -> str:
        return f"B{self.bloc.block_num}"
    
    @property
    def state_directory(self):
        state = self.state
        if state == '1':
            return 'Uncached'
        elif state == '2':
            return 'Shared'
        elif state == '3':
            return 'Modified'
        elif state == '4':
            return 'Invalid'
        else:
            return state
    
class CacheNode(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    bloc = models.ForeignKey(MemoryBloc, on_delete=models.CASCADE)
    state_cache = models.CharField(max_length=20, choices=state_block)

    def __str__(self) -> str:
        return f"{self.node.name} B{self.bloc.block_num}"
    
    @property
    def state_cache_state(self):
        state = self.state_cache
        if state == '2':
            return 'Shared'
        elif state == '3':
            return 'Modified'
        elif state == '4':
            return 'Invalid'
        else:
            return state
    
class MessageSimulation(models.Model):
    type_message = models.CharField(max_length=30, choices=msg_type_choice)
    source = models.CharField(max_length=30)
    destination = models.CharField(max_length=30)
    content_msg = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.type_message
    
    @property
    def message(self):
        index = int(self.type_message)
        index -= 1
        return msg_type_choice[index][1]