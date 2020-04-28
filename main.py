import pygame, sys, heapq
from pggrid import PGGrid

lastupdate = -1

width,height = 645,645
rows,cols = 10,10
gaps = 5
fps = 30

pygame.font.init()
font = pygame.font.Font('Roboto-Regular.ttf', 30)

source = None
target = None

grid = PGGrid(width,height,gaps=gaps)
status = pygame.Surface((450,645))
grid.setExtraSurfaces(None,status,None,None)

def create_nodes() :
    global nodes
    nodes = grid.createNodes(rows, cols, source=0, target=0, obstacle=0)

def reset_nodes() :
    for r in nodes :
        for n in r :
            n.__dict__.update({'visited':0, 'inqueue':0, 'parent':None})
            if not(n.source) and not(n.target) and not(n.obstacle) : n.image.fill((255,255,255))

create_nodes() #nodes

def write_status(lines) :
    status.fill((0,0,0))
    for i in range(len(lines)):
        try :
            textsurface = font.render(lines[i], True, (255, 255, 255))
            status.blit(textsurface,(0,i*30))
        except :
            pass

###pathfinding

step = False
runAll = False

def pathfinding_onkeypress(key,node) :
    global step,runAll
    if key==pygame.K_ESCAPE : grid.signalClose()
    if key==pygame.K_SPACE : step = True
    if key==pygame.K_1 : runAll = True

def get_neighbors_4dir(node) :
    neighbors = []
    for i,j in [(-1,0),(1,0),(0,-1),(0,1)] :
        if node.i+i>=0 and node.i+i<rows and node.j+j>=0 and node.j+j<cols and not(nodes[node.i+i][node.j+j].obstacle) :
            neighbors.append(nodes[node.i+i][node.j+j])
    return neighbors

def manhattan(u,v) :
    return abs(u.i-v.i)+abs(u.j-v.j)

class PQ :
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]
    
    def print(self) :
        for x in self.elements :
            print('p',x[0],'i',x[1].i,'j',x[1].j)
    
    def size(self) :
        return len(self.elements)

def astar() :
    global step,runAll
    if source is None or target is None :
        print("Please define source and target")
        return

    grid.setOnClick(None)
    grid.setOnDrop(None)
    grid.setOnKeyPress(pathfinding_onkeypress)
    reset_nodes()

    q = PQ()
    s = nodes[source[0]][source[1]]
    t = nodes[target[0]][target[1]]
    for r in nodes:
        for n in r:
            n.h=manhattan(n,t)
            n.g=sys.maxsize
    q.put(s, 0)
    s.g=0
    found = False
    done = False
    
    vcount=0
    finaldist="Computing..."

    u = None

    grid.open()
    while True :
        if not(found) and not(q.empty()) and (step or runAll) :
            u = q.get()
            vcount+=1
            if u.target :
                found=True
                finaldist = u.g
                continue
            if not(u.source) : u.image.fill((0,255,0))
            for v in get_neighbors_4dir(u) :
                c = u.g+1
                if c<v.g :
                    v.g = c
                    f = c+v.h
                    q.put(v,f)
                    if not(v.source) and not(v.target) :
                        v.image.fill((144,238,144))
                    v.parent = u
        
        if not(found) and (q.empty) :
            finaldist = "NO PATH"

        if not(done) and found and (step or runAll) :
            t = t.parent
            if t==s : done = True
            else : t.image.fill((255,0,0))
        
        step = False

        write_status([
            "A* Algorithm...",
            f"Queue size: {q.size()}",
            f"Visited nodes: {vcount}",
            f"Distance from s to t: {finaldist}",
            f"Visiting node: ({u.i if u is not None else source[0]},{u.j if u is not None else source[1]})",
            "Press SPACEBAR to step",
            "Press 1 to run",
            '',
            '',
            "Press ESC to exit"
        ])
        if not(grid.tick(fps)) :
            break

###pathfinding

def change_size() :
    global width,height,status
    width,height = int(input("new width: ")),int(input("new height: "))
    grid.setConstraints(width,height)
    status = pygame.Surface((450,height))
    grid.setExtraSurfaces(None,status,None,None)
    create_nodes()

def change_nodes_count() :
    global rows,cols
    rows,cols = int(input("new rows count: ")),int(input("new columns count: "))
    create_nodes()

def change_gaps() :
    global gaps
    gaps = int(input("new gaps size: "))
    grid.setConstraints(width,height,gaps)
    create_nodes()

def set_fps() :
    global fps
    fps = int(input("new fps: "))

def edit_grid() :
    grid.setOnClick(edit_onclick)
    grid.setOnDrop(edit_ondrop)
    grid.setOnKeyPress(edit_onkeypress)
    reset_nodes()
    grid.open()
    while True :
        write_status([
            f"Source: ({source[0]},{source[1]})" if source is not None else "Source not set",
            f"Target: ({target[0]},{target[1]})" if target is not None else "Target not set",
            "Press S to set Source",
            "Press T to set Target",
            "Click and drag to set obstacles",
            '',
            '',
            "Press ESC to exit"
        ])
        if not(grid.tick(30)) :
            break

def edit_onclick(node) :
    global lastupdate
    if lastupdate==-1 : lastupdate = node.obstacle
    if node.obstacle and node.obstacle==lastupdate :
        node.obstacle = 0
        node.image.fill((255,255,255))
    elif not(node.obstacle) and node.obstacle==lastupdate :
        node.obstacle = 1
        node.image.fill((0,0,0))

def edit_ondrop() :
    global lastupdate
    lastupdate = -1

def edit_onkeypress(key,node) :
    global source, target
    if key==pygame.K_ESCAPE : grid.signalClose()
    if len(node)==0 : return
    n = node[0]
    if not(n.source) and not(n.target) and not(n.obstacle) : 
        if key==pygame.K_s :
            if source is not None :
                u=nodes[source[0]][source[1]]
                u.source = 0
                u.image.fill((255,255,255))
            n.source = 1
            n.image.fill((0,0,255))
            source = (n.i,n.j)
        if key==pygame.K_t :
            if target is not None :
                u=nodes[target[0]][target[1]]
                u.target = 0
                u.image.fill((255,255,255))
            n.target = 1
            n.image.fill((160,32,240))
            target = (n.i,n.j)

def grid_start() :
    global step,runAll
    while True :
        step,runAll = False,False
        print(f"""Please input an option:
e/> edit obstacles and source/end point
f/> set fps
1/> A* pathfinding
q/> back""")
        gm = input("$ ")
        if gm=='q' : break
        elif gm=='e' : edit_grid()
        elif gm=='f' : set_fps()
        elif gm=='1' : astar()

def main_menu() :
    while True :
        print(f"""Please input a letter:
r/> change grid size (current {width}x{height})
n/> change node numbers (current {rows}x{cols})
g/> change gaps (current {gaps}px)
s/> start grid
q/> quit""")
        mm = input("$ ")
        if mm=='q' : exit(0)
        elif mm=='r' : change_size()
        elif mm=='n' : change_nodes_count()
        elif mm=='g' : change_gaps()
        elif mm=='s' : grid_start()

main_menu()
