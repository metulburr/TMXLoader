
import pygame as pg
from xml import sax
import sys
if sys.version[0] == '3':
    xrange = range

class Tileset:
    def __init__(self, file, tile_width, tile_height):
        image = pg.image.load(file).convert_alpha()
        if not image:
            print("Error creating new Tileset: file {} not found".format(file))
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles = []
        for line in xrange(int(image.get_height()/self.tile_height)):
            for column in xrange(int(image.get_width()/self.tile_width)):
                pos = pg.Rect(
                        column*self.tile_width,
                        line*self.tile_height,
                        self.tile_width,
                        self.tile_height )
                self.tiles.append(image.subsurface(pos))

    def get_tile(self, gid):
        return self.tiles[gid]

class TMXHandler(sax.ContentHandler):
    def __init__(self, debug=False):
        self.debug = debug
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0
        self.columns = 0
        self.lines  = 0
        self.properties = {}
        self.image = None
        self.tileset = None
        self.objects = {} #{objectname:[{'x':x, 'y':y, 'width':width, 'height':height]}
        self.key = None

    def startElement(self, name, attrs):
        # get most general map informations and create a surface
        if name == 'map':
            self.columns = int(attrs.get('width'))
            self.lines  = int(attrs.get('height'))
            self.tile_width = int(attrs.get('tilewidth'))
            self.tile_height = int(attrs.get('tileheight'))
            self.width = self.columns * self.tile_width
            self.height = self.lines * self.tile_height
            self.image = pg.Surface([self.width, self.height]).convert()
        # create a tileset
        elif name=="image":
            source = attrs.get('source')
            self.tileset = Tileset(source, self.tile_width, self.tile_height)
        # store additional properties.
        elif name == 'property':
            self.properties[attrs.get('name')] = attrs.get('value', None)
        # starting counting
        elif name == 'layer':
            self.line = 0
            self.column = 0
        # get information of each tile and put on the surface using the tileset
        elif name == 'tile':
            gid = int(attrs.get('gid')) - 1
            if gid < 0: 
                gid = 0
            tile = self.tileset.get_tile(gid)
            pos = (self.column*self.tile_width, self.line*self.tile_height)
            self.image.blit(tile, pos)

            self.column += 1
            if(self.column>=self.columns):
                self.column = 0
                self.line += 1
        elif name == 'objectgroup':
            self.line = 0
            self.column = 0
            self.key = attrs.get('name')
            self.objects[self.key] = []
        elif name == 'object':
            self.objects[self.key].append({
                    'x':attrs.get('x'),
                    'y':attrs.get('y'),
                    'width':attrs.get('width'),
                    'height':attrs.get('height'),
                }
            )
            
            self.column += 1
            if(self.column>=self.columns):
                self.column = 0
                self.line += 1

    # just for debugging
    def endDocument(self):
        if self.debug:
            print('width:{} height:{} tile width:{} tile height:{}'.format(self.width, self.height, self.tile_width, self.tile_height))
            print(self.image)
            print('properties: {}'.format(self.properties))
            
            if sys.version[0] == '2':
                items = self.objects.iteritems()
            else:
                items = self.objects.items()
            print('objects')
            for k,v in items:
                print('\t{}:{}'.format(k, len(v)))
                for index in v:
                    print('\t\t{}'.format(index))

if __name__ == "__main__": 
    class Control:
        def __init__(self):
            pg.init()
            self.screensize = (800,600)
            self.screen = pg.display.set_mode(self.screensize)
            self.screenrect = self.screen.get_rect()
            self.done = False
            self.parser = sax.make_parser()
            self.tmx = TMXHandler(debug=True)
            self.parser.setContentHandler(self.tmx)
            self.parser.parse(sys.argv[1])
            
        def events(self):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                elif event.type == pg.KEYDOWN:
                    self.done = True
                    
        def update(self):
            pass
            
        def render(self):
            self.screen.fill((255,255,255))
            self.screen.blit(self.tmx.image, (0,0))
            
        def run(self):
            while not self.done:
                self.events()
                self.update()
                self.render()
                pg.display.update()
            
    if len(sys.argv) != 2:
        print('To test: program requires tmx file as argument in same directory. Tileset location determined by tmx file.')
    else:
        app = Control()
        app.run()

