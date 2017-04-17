# -*- coding: utf-8 -*-

import math
import PIL
import random
import xml.etree.ElementTree as ET
import collections

class Model:
    def __init__(self, width, height):
        #initialize

        
        self.stationary = []
                

        self.FMX = width
        self.FMY = height
        self.T = 2
        #self.limit = 0
        
        self.rng = random.Random() #todo: set rng

        self.wave = [[[False for _ in range(self.T)] for _ in range(self.FMY)] for _ in range(self.FMX)]
        self.changes = [[False for _ in range(self.FMY)] for _ in range(self.FMX)]
        self.observed = None#[[0 for _ in range(self.FMY)] for _ in range(self.FMX)]

        self.log_prob = 0
        self.log_t = math.log(self.T)

    def Observe(self):
        print("---")
        print(self.observed)
        print(self.changes)
        print(self.stationary)
        print(self.wave)
        observed_min = 1e+3
        observed_sum = 0
        main_sum = 0
        log_sum = 0
        noise = 0
        entropy = 0
        
        argminx = -1
        argminy = -1
        amount = None
        w = []
        
        # Find the point of minimum entropy
        for x in range(0, self.FMX):
            for y in range(0, self.FMY):
                if self.OnBoundary(x, y):
                    pass
                else:
                    w = self.wave[x][y]
                    amount = 0
                    observed_sum = 0
                    t = 0
                    while t < self.T:
                        if w[t]:
                            amount += 1
                            observed_sum += self.stationary[t]
                        t += 1
                    if 0 == observed_sum:
                        print("w: {2} Observed Sum: {0}: {1}".format(observed_sum, self.stationary, w))
                        return False
                    noise = 1e-6 * self.rng.random()
                    if 1 == amount:
                        entropy = 0
                    elif self.T == amount:
                        entropy = self.log_t
                    else:
                        main_sum = 0
                        log_sum = math.log(observed_sum)
                        t = 0
                        while t < self.T:
                            if w[t]:
                                main_sum += self.stationary[t] * self.log_prob[t]
                            t += 1
                        entropy = log_sum - main_sum / observed_sum
                    if entropy > 0 and (entropy + noise < observed_min):
                        observed_min = entropy + noise
                        argminx = x
                        argminy = y
                    
        # No minimum entropy, so mark everything as being observed...
        print("No Min? {0}:{1}".format(argminx, argminy))
        if (-1 == argminx) and (-1 == argminy):
            self.observed = [[0 for _ in range(self.FMY)] for _ in range(self.FMX)]
            for x in range(0, self.FMX):
                self.observed[x] = [0 for _ in range(self.FMY)]
                for y in range(0, self.FMY):
                    for t in range(0, self.T):
                        if self.wave[x][y][t]:
                            self.observed[x][y] = t
                            break
            return True
        
        # A minimum point has been found, so prep it for propogation...
        distribution = [0 for _ in range(0,self.T)]
        print("distibution {0}".format(distribution))
        for t in range(0,self.T):
            distribution[t] = self.stationary[t] if self.wave[argminx][argminy][t] else 0
        r = StuffRandom(distribution, self.rng.random())
        print("r {0}".format(r))
        for t in range(0,self.T):
            self.wave[argminx][argminy][t] = (t == r)
        self.changes[argminx][argminy] = True
        return None
        
#        for x in range(0, self.FMX):
#            for y in range(0, self.FMY):
#                if self.OnBoundary(x,y):
#                    pass
#                else:
#                    w = self.wave[x][y]
#                    amount = 0
#                    observed_sum = 0
#                    for t in range(0, self.T):
#                        if True == w[t]:
#                            amount += 1
#                            observed_sum += self.stationary[t]
#                    if 0 == observed_sum:
#                        return False
#                    noise = 1e-6 * self.rng.random()
#                    if(1 == amount):
#                        entropy = 0
#                    else:
#                        if (self.T == amount):
#                            entropy = self.log_t
#                        else:
#                            main_sum = 0
#                            log_sum = math.log(observed_sum)
#                            for t in range(0, self.T):
#                                if w[t]:
#                                    main_sum += self.stationary[t] * self.log_prob[t]
#                                entropy = log_sum - main_sum / observed_sum
#                    if ((entropy > 0) and ((entropy + noise) < observed_min)):
#                        observed_min = entropy + noise
#                        argminx = x
#                        argminy = y
#        if (-1 == argminx) and (-1 == argminy):
#            self.observed = [[0 for _ in range(self.FMY)] for _ in range(self.FMX)]
#            for x in range(0, self.FMX):
#                self.observed[x] = [None for _ in range(self.FMY)]
#                for y in range(0, self.FMY):
#                    for t in range(0, self.T):
#                        if self.wave[x][y][t]:
#                            self.observed[x][y] = t
#                            break
#            return True
#        distribution = [None for _ in range(self.T)]
#        for t in range(0, self.T):
#            if self.wave[argminx][argminy][t]:
#                distribution[t] = self.stationary[t]
#            else:
#                distribution[t] = 0
#        r = StuffRandom(distribution, self.rng.random())
#        for t in range(0, self.T):
#            self.wave[argminx][argminy][t] = (t == r)
#        self.changes[argminx][argminy] = True
#        return None
        
    def Run(self, seed, limit):
        self.log_t = math.log(self.T)
        self.log_prob = [0 for _ in range(self.T)]
        for t in range(0,self.T):
            self.log_prob[t] = math.log(self.stationary[t])
        self.Clear()
        self.rng = random.Random()
        self.rng.seed(seed)
        l = 0
        while (l < limit) or (0 == limit): # if limit == 0, then don't stop
            l += 1
            print("Observe")
            result = self.Observe()
            print("Observe result: {0}".format(result))
            print("--->")
            print(self.observed)
            print(self.changes)
            print(self.stationary)
            print(self.wave)
            if None != result:
                return result
            pcount = 0
            presult = True
            while(presult):
                presult = self.Propogate()
                #print(pcount)
                pcount += 1
                print("Propogate: {0}".format(pcount))
                pass
        return True
            
        
    def Propogate(self):
        return False
        
    def Clear(self):
        for x in range(0,self.FMX):
            for y in range(0, self.FMY):
                for t in range(0, self.T):
                    self.wave[x][y][t] = True
                self.changes[x][y] = False
    
                
    def OnBoundary(self, x, y):
        return True # Abstract, replaced in child classes
        
    def Graphics(self):
        return PIL.Image.new("RGB",(self.FMX, self.FMY),(0,0,0))
    
class OverlappingModel(Model):
    #def __init__(self, width, height):
    #    super( OverlappingModel, self).__init__(width, height)
    #    self.propogator = [[[[]]]]
    #    self.N = 0
    #    self.patterns= [[]]
    #    self.colors = []
    #    self.ground = 0
        
    def __init__(self, width, height, name, N_value = 2, periodic_input_value = True, periodic_output_value = False, symmetry_value = 8, ground_value = 0):
        super( OverlappingModel, self).__init__(width, height)
        self.propogator = [[[[]]]]
        self.N = N_value
        self.periodic = periodic_output_value
        self.bitmap = PIL.Image.open("samples/{0}.png".format(name))
        self.SMX = self.bitmap.size[0]
        self.SMY = self.bitmap.size[1]
        self.sample = [[0 for _ in range(self.SMY)] for _ in range(self.SMX)]
        self.colors = []
        for y in range(0, self.SMY):
            for x in range(0, self.SMX):
                a_color = self.bitmap.getpixel((x, y))
                color_exists = [c for c in self.colors if c == a_color]
                if len(color_exists) < 1:
                    self.colors.append(a_color)
                #print("{0}, {1}, {2}, {3}".format(x, y, self.SMX, self.SMY))
                samp_result = [i for i,v in enumerate(self.colors) if v == a_color]
                self.sample[x][y] = samp_result
                #for i, v in enumerate(self.colors): 
                #    if v == a_color:
                #        print("{0}, {1}: {2} -> {3}\t\t= {4}".format(x, y, i, v, self.sample[x][y]))
                
        self.color_count = len(self.colors)
        #print("Colors: {0}".format(self.colors))
        self.W = StuffPower(self.color_count, self.N * self.N)
        
        self.patterns= [[]]
        self.ground = 0
        
        def FuncPattern(passed_func):
            result = [0 for _ in range(self.N * self.N)]
            for y in range(0, self.N):
                for x in range(0, self.N):
                    result[x + (y * self.N)] = passed_func(x, y)
            #print("Pattern: {0}".format(result))
            return result
            
        pattern_func = FuncPattern
            
        def PatternFromSample(x, y):
            def innerPattern(dx, dy):
                #print("PatternFromSample {0},{1}:{2}".format(dx, dy, self.sample[(x + dx) % self.SMX][(y + dy) % self.SMY]))
                return self.sample[(x + dx) % self.SMX][(y + dy) % self.SMY]
            return pattern_func(innerPattern)
        def Rotate(p):
            return FuncPattern(lambda x, y: p[self.N - 1 - y + x * self.N])
        def Reflect(p):
            return FuncPattern(lambda x, y: p[self.N - 1 - x + y * self.N])
            
        def Index(p):
            #print("Index: {0}".format(p))
            result = 0
            power = 1
            for i in range(0, len(p)):
                result = result + (sum(p[len(p) - 1 - i]) * power)
                power = power * self.color_count
            #print("Index Result: {0}".format(result))
            return result

                                    
            
        def PatternFromIndex(ind):
            residue = ind
            power = self.W
            result = [None for _ in range(self.N * self.N)]
            for i in range(0, len(result)):
                power = power / self.color_count
                count = 0
                while residue >= power:
                    residue = residue - power
                    count = count + 1
                result[i] = count
            return result
            
        self.weights = collections.Counter()
        ordering = []
        
        ylimit = self.SMY - self.N + 1
        xlimit = self.SMX - self.N + 1
        if True == periodic_input_value:
            ylimit = self.SMY
            xlimit = self.SMX
        for y in range (0, ylimit):
            for x in range(0, xlimit):
                ps = [0 for _ in range(8)]
                ps[0] = PatternFromSample(x,y)
                ps[1] = Reflect(ps[0])
                ps[2] = Rotate(ps[0])
                ps[3] = Reflect(ps[2])
                ps[4] = Rotate(ps[2])
                ps[5] = Reflect(ps[4])
                ps[6] = Rotate(ps[4])
                ps[7] = Reflect(ps[6])
                #print("ps: {0}".format(ps))
                for k in range(0,symmetry_value):
                    ind = Index(ps[k])
                    indexed_weight = collections.Counter({ind : 1})
                    self.weights = self.weights + indexed_weight
        ordering = list(self.weights.keys())
                        
        #print(self.weights)
        self.T = len(self.weights)
        self.ground = (self.ground + self.T) % self.T
        
        self.patterns = [[None] for _ in range(self.T)]
        self.stationary = [None for _ in range(self.T)]
        self.propogator = [[[[0]]] for _ in range(2 * self.N - 1)]
        
        counter = 0
        #print(ordering)
        for w in ordering:
            self.patterns[counter] = PatternFromIndex(w)
            self.stationary[counter] = self.weights[w]
            counter += 1
            
        for x in range(0, self.FMX):
            for y in range(0, self.FMY):
                self.wave[x][y] = [False for _ in range(self.T)]
                
        def Agrees(p1, p2, dx, dy):
            xmin = dx
            xmax = self.N
            if dx < 0:
                xmin = 0
                xmax = dx + self.N
            ymin = dy
            ymax = self.N
            if dy < 0:
                ymin = 0
                ymax = dy + self.N
            for y in range(ymin, ymax):
                for x in range(xmin, xmax):
                    if p1[x + self.N * y] != p2[x - dx + self.N * (y - dy)]:
                        return False
            return True

        for x in range(0, 2 * self.N - 1):
            self.propogator[x] = [[[0]] for _ in range(2 * self.N - 1)]
            for y in range(0, 2 * self.N - 1):
                self.propogator[x][y] = [[0] for _ in range(self.T)]
                                  
                for t in range(0, self.T):
                    a_list = []
                    for t2 in range(0, self.T):
                        if Agrees(self.patterns[t], self.patterns[t2], x - self.N + 1, y - self.N + 1):
                            a_list.append(t2)
                    self.propogator[x][y][t] = [0 for _ in range(len(a_list))]
                    for c in range(0, len(a_list)):
                        self.propogator[x][y][t][c] = a_list[c]
        return
                    
    def OnBoundary(self, x, y):
        return (not self.periodic) and ((x + self.N > self.FMX ) or (y + self.N > self.FMY))
    
    def Propogate(self):
        print("Propogate")
        change = False
        b = False
        
        #x2 = None
        #y2 = None
        for x1 in range(0, self.FMX):
            for y1 in range(0, self.FMY):
                if (self.changes[x1][y1]):
                    self.changes[x1][y1] = False
                    dx = (0 - self.N) + 1
                    while dx < self.N:
                    #for dx in range(1 - self.N, self.N):
                        dy = (0 - self.N) + 1
                        while dy < self.N:
                        #for dy in range(1 - self.N, self.N):
                            x2 = x1 + dx
                            if x2 < 0:
                                x2 += self.FMX
                            elif x2 >= self.FMX:
                                    x2 -= self.FMX
                            y2 = y1 + dy
                            if y2 < 0:
                                y2 += self.FMY
                            elif y2 >= self.FMY:
                                    y2 -= self.FMY
                                    
                            if (not self.periodic) and (x2 + self.N > self.FMX or y2 + self.N > self.FMY):
                                pass
                            else:
                            
                                w1 = self.wave[x1][y1]
                                w2 = self.wave[x2][y2]
                                
                                p = self.propogator[(self.N - 1) - dx][(self.N - 1) - dy]
                                
                                for t2 in range(0,self.T):
                                    #print("w2[t2]: {0}".format(w2[t2]))
                                    if (not w2[t2]):
                                        pass
                                    else:
                                        b = False
                                        prop = p[t2]
                                        #print("prop: {0}".format(prop))
                                        i_one = 0
                                        while (i_one < len(prop)) and (False == b):
                                            b = w1[prop[i_one]]
                                            i_one += 1                                    
                                        if False == b:
                                            self.changes[x2][y2] = True
                                            change = True
                                            w2[t2] = False
                            dy += 1
                        dx += 1

        #print(change)                                    
        return change
        
    def Graphics(self):
        print("--- Graphics ---")
        print(self.observed)
        print(self.changes)
        print(self.stationary)
        print(self.wave)
        result = PIL.Image.new("RGB",(self.FMX, self.FMY),(0,0,0))
        bitmap_data = list(result.getdata())#[None] * (result.height * result.width)
        print("Graphics:observed: {0}".format(self.observed))
        if(self.observed != None):
            for y in range(0, self.FMY):
                dy = self.N - 1
                if (y < (self.FMY - self.N + 1)):
                    dy = 0
                for x in range(0, self.FMX):
                    dx = 0
                    if (x < (self.FMX - self.N + 1)):
                        dx = self.N - 1
                    local_obsv = self.observed[x - dx][y - dy]
                    #print(local_obsv)
                    local_patt = self.patterns[local_obsv][dx + dy * self.N]
                    c = self.colors[local_patt]
                    #print("{0} {1} {2} {3} ({4}, {5}) = {6}".format(x, y, dx, dy, x - dx, y - dy, local_patt))
                    #print(c, end="")
                    #bitmap_data[x + y * self.FMX] = (0xff000000 | (c.R << 16) | (c.G << 8) | c.B)
                    if isinstance(c, (int, float)):
                        bitmap_data[x + y * self.FMX] = (c, c, c)
                    else:
                        bitmap_data[x + y * self.FMX] = (c[0], c[1], c[2])
                #print("")
                    
        else:
            print("Graphics: wave:\n{0}".format(self.wave))
            for y in range(0, self.FMY):
                for x in range(0, self.FMX):
                    contributors = 0
                    r = 0
                    g = 0
                    b = 0
                    for dy in range(0, self.N):
                        for dx in range(0, self.N):
                            sx = x - dx
                            if sx < 0:
                                sx += self.FMX
                            sy = y - dy
                            if sy < 0:
                                sy += self.FMY
                            if (self.OnBoundary(sx, sy)):
                                pass
                            else:
                                for t in range(0, self.T):
                                    #print("wave: {0},{1},{2}: {3}".format(sx, sy, t, self.wave[sx][sy][t]))
                                    if self.wave[sx][sy][t]:
                                        contributors += 1
                                        #print(list(self.colors))
                                        color = self.colors[self.patterns[t][dx + dy * self.N]]
                                        if isinstance(color, (int, float)):
                                            r = int(color)
                                            g = int(color)
                                            b = int(color)
                                        else:
                                            r += int(color[0])#.R
                                            g += int(color[1])#.G
                                            b += int(color[2])#.B
                    #bitmap_data[x + y * self.FMX] = (0xff000000 | ((r / contributors) << 16) | ((g / contributors) << 8) | (b / contributors))
                    if contributors > 0:
                        bitmap_data[x + y * self.FMX] = (int(r / contributors), int(g / contributors), int(b / contributors))
                    else:
                        print("WARNING: No contributors")
                        bitmap_data[x + y * self.FMX] = (int(r), int(g), int(b))
        result.putdata(bitmap_data)
        return result
        
    def Clear(self):
        super(OverlappingModel, self).Clear()
        if(self.ground != 0 ):
            for x in range(0, self.FMX):
                for t in range(0, self.T):
                    if t != self.ground:
                        self.wave[x][self.FMX - 1][t] = False
                    self.changes[x][self.FMX - 1] = True
                    
                    for y in range(0, self.FMY - 1):
                        self.wave[x][y][self.ground] = False
                        self.changes[x][y] = True
            while self.Propogate():
                pass
            
                        
                        
                    
class SimpleTiledModel(Model):
    def __init__(self, width, height, name, subset_name, periodic_value, black_value):
        super( OverlappingModel, self).__init__(width, height)
        self.propogator = [[[]]]
        self.tiles = []
        self.tilenames = []
        self.tilesize = 0
        self.black = False
        self.periodic = periodic_value
        self.black = black_value
        

        

#def getNextRandom():
#    return random.random()
    
def StuffRandom(source_array, random_value):
    a_sum = sum(source_array)
    
    if 0 == a_sum:
        for j in range(0, len(source_array)):
            source_array[j] = 1
        a_sum = sum(source_array)
    for j in range(0, len(source_array)):
        source_array[j] /= a_sum
    i = 0
    x = 0
    while (i < len(source_array)):
        x += source_array[i]
        if random_value <= x:
            return i
        i += 1
    return 0
    
def StuffPower(a, n):
    product = 1
    for i in range(0, n):
        product *= a
    return product
    
# TODO: finish StuffGet
def StuffGet(xml_node, xml_attribute, default_t):
    s = ""
    if s == "":
        return default_t
    return s
    
def string2bool(strn):
    if isinstance(strn, bool):
        return strn
    return strn.lower() in ["true"]
    
class Program:
    def __init__(self):
        pass
    
    def Main(self):
        self.random = random.Random()
        xdoc = ET.ElementTree(file="samples.xml")
        counter = 1
        for xnode in xdoc.getroot():
            if("#comment" == xnode.tag):
                continue
            a_model = None
            
            name = xnode.get('name', "NAME")
            print("< {0} ".format(name), end='')
            if "overlapping" == xnode.tag:
                #print(xnode.attrib)
                a_model = OverlappingModel(int(xnode.get('width', 48)), int(xnode.get('height', 48)), xnode.get('name', "NAME"), int(xnode.get('N', 2)), string2bool(xnode.get('periodicInput', True)), string2bool(xnode.get('periodic', False)), int(xnode.get('symmetry', 8)), int(xnode.get('ground',0)))
                pass
            else:
                if "simpletiled" == xnode.tag:
                    print("> ", end="\n")
                    continue
                else:
                    continue
            
            for i in range(0, int(xnode.get("screenshots", 2))):
                for k in range(0, 10):
                    print("> ", end="")
                    seed = self.random.random()
                    finished = a_model.Run(seed, int(xnode.get("limit", 0)))
                    if finished:
                        print("DONE")
                        a_model.Graphics().save("{0} {1} {2}.png".format(counter, name, i), format="PNG")
                        break
                    else:
                        print("CONTRADICTION")
            counter += 1
            #print(xnode)
            #print(xnode.attrib)
        
    
prog = Program()    
prog.Main()

#a_model = OverlappingModel(8, 8, "Chess", 2, True, True, 8,0)
#a_model = OverlappingModel(48, 48, "Hogs", 3, True, True, 8,0)
#gseed = random.Random()
#finished = a_model.Run(364, 0)
#if(finished):
#    test_img = a_model.Graphics()
#else:
#    print("CONTRADICTION")
#test_img