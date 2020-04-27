import sys,pygame

class PGGrid(object) :
    class PGNode(pygame.sprite.Sprite) :
        def __init__(self, i:int, j:int, w:int, h:int, x:int, y:int, color:tuple, group:pygame.sprite.Group, extraProprieties:dict) :
            pygame.sprite.Sprite.__init__(self, group)
            self.image = pygame.Surface((w,h))
            self.image.fill(color)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.i = i
            self.j = j
            self.itupdateable = True
            self.__dict__.update(extraProprieties)
        
        def update(self, updateable:bool)->None :
            self.itupdateable = updateable
        
        def __lt__(self,other) :
            return 0
        
        def print(self) :
            print(self.i,self.j)

    def __init__(self, width:int, height:int, bgColor:tuple=(0,0,0), gaps:int=0) :
        pygame.init()
        self._width = width
        self._height = height
        self._bgColor = bgColor
        self._gaps = gaps
        self._onClick = None
        self._onDrop = None
        self._onKeyPress = None
        self._onRightClick = None
        self._nodes = None
        self._topSurface = None
        self._rightSurface = None
        self._bottomSurface = None
        self._leftSurface = None
    
    def setExtraSurfaces(self, top:pygame.Surface, right:pygame.Surface, bottom:pygame.Surface, left:pygame.Surface)->None :
        self._topSurface = top
        self._rightSurface = right
        self._bottomSurface = bottom
        self._leftSurface = left
    
    def setConstraints(self, width:int, height:int, gaps:int=0)->None :
        self._width = width
        self._height = height
        self._gaps = gaps

    def createNodes(self, rows:int, columns:int, color:tuple=(255,255,255), **nodeProprieties)->list :
        self._nodes = pygame.sprite.Group()
        w = (self._width-self._gaps*(columns-1))/columns
        h = (self._height-self._gaps*(rows-1))/rows
        if w!=int(w) : print("WARNING: floating point width for nodes.")
        if h!=int(h) : print("WARNING: floating point height for nodes.")
        nodes = []
        for i in range(rows) :
            t = []
            for j in range(columns) :
                x=w*j+self._gaps*j
                if self._leftSurface is not None : x+=self._leftSurface.get_rect().w
                y=h*i+self._gaps*i
                if self._topSurface is not None : y+=self._topSurface.get_rect().h
                t.append(self.PGNode(i,j,w,h,x,y,color,self._nodes,nodeProprieties))
            nodes.append(t)
        return nodes
    
    def setOnClick(self, func)->None :
        self._onClick = func
    
    def setOnRightClick(self, func)->None :
        self._onRightClick = func
    
    def setOnDrop(self, func)->None :
        self._onDrop = func
    
    def setOnKeyPress(self, func)->None :
        self._onKeyPress = func
    
    def _onClickNodes(self,nodes)->None :
        for n in nodes:
            n.update(False)
            self._onClick(n)

    def open(self)->None :
        width=self._width
        height=self._height

        if self._rightSurface is not None :
            width+=self._rightSurface.get_rect().w
            self._rightSurfaceRect = self._rightSurface.get_rect()
            self._rightSurfaceRect.x = self._width
            if self._leftSurface is not None : self._rightSurfaceRect.x+=self._leftSurface.get_rect().w

        if self._leftSurface is not None :
            width+=self._leftSurface.get_rect().w
            self._leftSurfaceRect = self._leftSurface.get_rect()

        if self._bottomSurface is not None :
            height+=self._bottomSurface.get_rect().h
            self._bottomSurfaceRect = self._bottomSurface.get_rect()
            self._bottomSurfaceRect.y = self._width
            if self._topSurface is not None : self._bottomSurfaceRect.y+=self._topSurface.get_rect().h

        if self._topSurface is not None :
            height+=self._topSurface.get_rect().h
            self._topSurfaceRect = self._topSurface.get_rect()
        
        self._screen = pygame.display.set_mode((width,height))
        self._screen.fill(self._bgColor)
        self._lastitClicked=False

        self.clock = pygame.time.Clock()

        self.quit = 0
    
    def signalClose(self)->None :
        self.quit = 1

    def tick(self, maxframes:int)->bool :
        if self.quit : pygame.display.quit(); return False
        
        for event in pygame.event.get() :
            if event.type == pygame.QUIT : pygame.quit(); return False
            if event.type == pygame.KEYDOWN and self._onKeyPress is not None : self._onKeyPress(event.key,[s for s in self._nodes.sprites() if s.rect.collidepoint(pygame.mouse.get_pos()) and s.itupdateable])
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self._onRightClick is not None :
                t = [s for s in self._nodes.sprites() if s.rect.collidepoint(pygame.mouse.get_pos())]
                if len(t)>0 : self._onRightClick(t[0])

        if self._onClick is not None : 
            if pygame.mouse.get_pressed()[0] :
                pos = pygame.mouse.get_pos()
                clicked_sprites = [s for s in self._nodes.sprites() if s.rect.collidepoint(pos) and s.itupdateable]
                self._onClickNodes(clicked_sprites)
                self._lastitClicked = True
            elif self._lastitClicked :
                self._lastitClicked = False
                self._nodes.update(True)
                if self._onDrop is not None : self._onDrop()
        
        self._screen.fill((0,0,0))
        if self._nodes is not None : self._nodes.draw(self._screen)

        if self._rightSurface is not None :
            self._screen.blit(self._rightSurface,self._rightSurfaceRect)

        if self._leftSurface is not None :
            self._screen.blit(self._leftSurface,self._leftSurfaceRect)

        if self._bottomSurface is not None :
            self._screen.blit(self._bottomSurface,self._bottomSurfaceRect)

        if self._topSurface is not None :
            self._screen.blit(self._topSurface,self._topSurfaceRect)

        pygame.display.update()

        self.clock.tick(maxframes)

        return True
