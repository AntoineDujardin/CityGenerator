import random

import block
#import ground

class City:
    """Class managing the creation of the whole city."""
    
    def __init__(self, citySizeX, citySizeY, minBlockSize,
                 maxBlockSize, roadSize):
        """Create the city"""
        
        # save the values
        self.citySizeX = citySizeX # >= minBS
        self.citySizeY = citySizeY # >= minBS
        self.minBlockSize = minBlockSize # >= 1
        self.maxBlockSize = maxBlockSize # >= 2*minBS+rS
        self.roadSize = roadSize # should be >= 1
        
        # initialize
        self.blocks = []
        self.roads = []
        
        # <create ground>
        
        # make the block decomposition
        self.cutBlocks(-self.citySizeX/2, self.citySizeX,
                       -self.citySizeY/2, self.citySizeY, roadSize)
    
    
    def __del__(self):
        """Cleanly delete the city"""
        
        # <del ground>
        
        # <del everything else>
    
    
    def cutBlocks(self, xStart, xSize, yStart, ySize, roadSize):
        """Recursively cut the city in blocks and roads"""
        
        if (xSize <= self.maxBlockSize and ySize <= self.maxBlockSize):
            # block should not be cutted further, create it
            self.blocks.append(block.Block([
                (xStart, yStart, 0),
                (xStart+xSize, yStart, 0),
                (xStart+xSize, yStart+ySize, 0),
                (xStart, yStart+ySize, 0)
            ]))
        
        elif (xSize <= self.maxBlockSize): # y cut
            yRoadSize = self.corrected(roadSize, ySize)
            yCut = random.uniform(self.minBlockSize,
                                  ySize-2*self.minBlockSize-yRoadSize)
            self.cutBlocks(xStart, xSize, yStart, yCut,
                           self.decreased(yRoadSize))
            #self.roads.append(road.Road(xStart, xSize, yStart+yCut,
            #                        yRoadSize))
            self.cutBlocks(xStart, xSize, yStart+yCut+yRoadSize,
                           ySize-yCut-yRoadSize,
                           self.decreased(yRoadSize))
        
        elif (ySize <= self.maxBlockSize): # x cut
            xRoadSize = self.corrected(roadSize, xSize)
            xCut = random.uniform(self.minBlockSize,
                                  xSize-2*self.minBlockSize-xRoadSize)
            self.cutBlocks(xStart, xCut, yStart, ySize,
                           self.decreased(xRoadSize))
            #mRoads.push(new Element(xStart+xCut, xRoadSize, yStart,
            #                        ySize))
            self.cutBlocks(xStart+xCut+xRoadSize, xSize-xCut-xRoadSize,
                           yStart, ySize, self.decreased(xRoadSize))
        
        else: # double cut
            xRoadSize = self.corrected(roadSize, xSize)
            yRoadSize = self.corrected(roadSize, ySize)
            nextRoadSize = self.decreased(min(xRoadSize, yRoadSize))
            xCut = random.uniform(self.minBlockSize,
                                  xSize-2*self.minBlockSize-xRoadSize)
            yCut = random.uniform(self.minBlockSize,
                                  ySize-2*self.minBlockSize-yRoadSize)
            
            self.cutBlocks(xStart, xCut, yStart, yCut, nextRoadSize)
            #mRoads.push(new Element(xStart+xCut, xRoadSize, yStart,
            #                        yCut))
            self.cutBlocks(xStart+xCut+xRoadSize, xSize-xCut-xRoadSize,
                           yStart, yCut, nextRoadSize)
            
            #mRoads.push(new Element(xStart, xSize, yStart+yCut,
            #                        yRoadSize))
            
            self.cutBlocks(xStart, xCut, yStart+yCut+yRoadSize,
                           ySize-yCut-yRoadSize, nextRoadSize)
            #mRoads.push(new Element(xStart+xCut, xRoadSize,
            #                        yStart+yCut+yRoadSize,
            #                        ySize-yCut-yRoadSize))
            self.cutBlocks(xStart+xCut+xRoadSize, xSize-xCut-xRoadSize,
                           yStart+yCut+yRoadSize, ySize-yCut-yRoadSize,
                           nextRoadSize)
    
    
    def corrected(self, roadSize, blockSize):
        """Return the roadSize after correction with regard to the
        blockSize : if the road is too big, decrease it."""
        
        return min(roadSize, blockSize-2*self.minBlockSize)
    
    
    def decreased(self, roadSize):
        """Return a decreased roadSize."""
        
        return (roadSize+1)/2
    
