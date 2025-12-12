import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

def create_er_diagram():
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Определяем сущности и их атрибуты
    entities = {
        'User': ['id (PK)', 'email', 'password_hash', 'role', 'created_at'],
        'Contact': ['id (PK)', 'name', 'email', 'phone', 'created_at', 'source'],
        'Deal': ['id (PK)', 'title', 'stage', 'budget', 'contact_id (FK)', 'user_id (FK)'],
        'Task': ['id (PK)', 'title', 'type', 'due_date', 'contact_id (FK)', 'deal_id (FK)'],
        'Document': ['id (PK)', 'name', 'type', 'file_path', 'deal_id (FK)']
    }
    
    positions = {
        'User': (1, 4),
        'Contact': (1, 2),
        'Deal': (3, 3),
        'Task': (3, 1),
        'Document': (5, 3)
    }
    
    colors = ['#FFEAA7', '#DDA0DD', '#98D8C8', '#85C1E9', '#F7DC6F']
    
    # Рисуем сущности
    for i, (entity, attrs) in enumerate(entities.items()):
        x, y = positions[entity]
        color = colors[i % len(colors)]
        
        # Прямоугольник для сущности
        rect = Rectangle((x, y), 2, 0.5 + len(attrs) * 0.2, 
                        facecolor=color, alpha=0.7, edgecolor='black')
        ax.add_patch(rect)
        
        # Название сущности
        ax.text(x + 1, y + 0.5 + len(attrs) * 0.2 - 0.1, entity, 
                fontweight='bold', ha='center', va='bottom', fontsize=10)
        
        # Атрибуты
        for j, attr in enumerate(attrs):
            ax.text(x + 0.1, y + 0.5 + len(attrs) * 0.2 - 0.3 - j * 0.2, attr,
                   fontsize=8, va='center')
    
    # Рисуем связи
    relationships = [
        ('User', 'Deal', '1:N'),
        ('Contact', 'Deal', '1:N'),
        ('Contact', 'Task', '1:N'),
        ('Deal', 'Task', '1:N'),
        ('Deal', 'Document', '1:N')
    ]
    
    for from_ent, to_ent, rel_type in relationships:
        x1, y1 = positions[from_ent]
        x2, y2 = positions[to_ent]
        
        # Линия связи
        ax.plot([x1 + 2, x2], [y1 + 0.3, y2 + 0.3], 'k-', linewidth=2)
        
        # Тип связи
        mid_x = (x1 + 2 + x2) / 2
        mid_y = (y1 + 0.3 + y2 + 0.3) / 2
        ax.text(mid_x, mid_y, rel_type, fontweight='bold', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
    
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 5)
    ax.set_title('ER-диаграмма: Основные сущности CRM', fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.show()

create_er_diagram()