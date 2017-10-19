#!/usr/bin/env python
''' Author  : Huy Nguyen
    Program : Boostrapping
    Start   : 09/10/2017
    End     : 09/18/2016
'''
from itertools import chain, combinations
from ete3 import Tree
import argparse
from findParent_local import setOfBlocks,setOfGene




def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--Operon","-i", help="Operon file name")
    parser.add_argument("--outDir","-o", help="Output Directory for the bootstrap")
#    parser.add_argument("--ref","-r", help="reference genome (ncbi accession number)")
    args = parser.parse_args()
    return args



### generate the powerset of a given set
def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(1,len(xs)))
    
    ### given the reference gene block, the current initial gene block of the inner node, generate the sample to test
    

### find the relevant gene block
'''@function: given initial block and its 2 children block,calculate the relevant gene block
   @input   : block, intersection
   @output  : string
'''     
def relevant(block,intersection):
    string = ""
    for letter in block:
        if letter == "|":
            string+=letter
        else:
            if letter in intersection:
                string+=letter
    return string

### calculate split
def getSplit(string):
    count = 0
    block = setOfBlocks(string)
    for item in block:
        if len(block)!= 0:
            count+=1
    return count
### check if the new gene block is valid,
def isValid(block):
    blocks = setOfBlocks(block)
    check  = False
    for item in blocks:
        if len(item)>=2:
            return True
    return check
### if the block is valid, reformat the block
def reformat(block):
    blocks = setOfBlocks(block)
    res = []

    for item in blocks:
        if len(item)>0:
            res.append(''.join(sorted(item)))

    return '|'.join(res)
### get the duplicated gene set of a given block
def getDuplication(string):
    dup = set()
    block = setOfBlocks(string)
    for item in block:
        dic = {}
        for letter in item:
            if letter not in dic:
                dic[letter]=1
            else:
                dup.add(letter)
    return dup
### class block to store geneblock info
class Block(object):
    def __init__(self,geneBlock,deletion,duplication ,split):
        self.geneBlock = geneBlock
        self.deletion = deletion
        self.duplication = duplication
        self.split  = split
    
    def calculateDistance(self,geneBlock):
        genes1 = setOfGene(self.geneBlock)
        genes2 = setOfGene(geneBlock)
        del_distance = len(genes1.symmetric_difference(genes2))
        intersection = genes1.intersection(genes2)
        deletion = [del_distance,self.getDeletion()]
            
        # remove gene that is not in itnersection
        string1 = reformat(relevant(geneBlock,intersection))
        string2 = reformat(relevant(self.geneBlock,intersection))
        
        # duplciation
        dup1 = getDuplication(string1)
        dup2 = getDuplication(string2)
        duplication = [abs(len(dup1)-len(dup2)),self.getDupication()]
        
        # split
        count1 = getSplit(string1)
        count2 = getSplit(string2)
        split = [abs(count1-count2),self.getSplit()]     
        
        distance = [deletion,duplication,split]      
        return distance
    
    def getDeletion(self):
        return int(self.deletion.split('|')[1])

    def getDupication(self):
        return int(self.duplication.split('|')[1])

    def getSplit(self):
        return int(self.split.split('|')[1])        
'''@function: given ref block, and current innitial, generate possible suboptimal sets
   @input   : string1, string2
   @output  : set of strings
'''   
def generateSample(node):
    res = {}
    geneInit = setOfGene(node.initial)
    children = [child for child in node.get_children()]
    childrenBlock  = []
    for child in children:
        if child.is_leaf():
            newBlock = Block(child.gene_block,child.deletion,child.duplication,child.split)
            childrenBlock.append(newBlock)
        else:
            newBlock = Block(child.initial,child.deletion,child.duplication,child.split)
            childrenBlock.append(newBlock)
    geneChild = [setOfGene(child.geneBlock) for child in childrenBlock]

    unionGenes = geneChild[0].union(geneChild[1])
    intersectionGenes = geneChild[0].intersection(geneChild[1])
    if geneInit == unionGenes:
        
        for gene in geneInit:
        
            temp = (node.initial).replace(gene,"")
            if not isValid(temp):
                continue
            if temp in res or temp == node.initial:
                continue
            temp = reformat(temp)
            distance1 = childrenBlock[0].calculateDistance(temp)
            distance2 = childrenBlock[1].calculateDistance(temp)
                                  
            distance = []
            for i in range(3):
                dist = []
                dist.append(distance1[i][0]+distance2[i][0])
                dist.append(dist[0]+distance1[i][1]+distance2[i][1])
                distance.append(dist)
            res[temp] = distance
    else:
        onlyOne = unionGenes-intersectionGenes
        powerSet = powerset(onlyOne)
        for subset in powerSet:
            # add to our initial
            toAdd = []
            toRemove = []
            for gene in subset:
                if gene not in node.initial:
                    toAdd.append(gene)
                else:
                    toRemove.append(gene)
            # add new gene to initial, this needs more logic
            if len(toAdd) >0:
                temp = node.initial
                for gene in toAdd:
                    temp +=gene
                if temp != node.initial:
                    
                    distance1 = childrenBlock[0].calculateDistance(temp)
                    distance2 = childrenBlock[1].calculateDistance(temp)
                    distance = []
                    for i in range(3):
                        dist = []
                        dist.append(distance1[i][0]+distance2[i][0])
                        dist.append(dist[0]+distance1[i][1]+distance2[i][1])
                        distance.append(dist)
                    res[temp] = distance
            # remove the gene from initial
            if len(toRemove) >0:
                temp = node.initial
                for gene in toRemove:
                    temp.replace(gene,"")
                if not isValid(temp) or temp == node.initial:
                    continue
                distance1 = childrenBlock[0].calculateDistance(temp)
                distance2 = childrenBlock[1].calculateDistance(temp)
                distance = []
                for i in range(3):
                    dist = []
                    dist.append(distance1[i][0]+distance2[i][0])
                    dist.append(dist[0]+distance1[i][1]+distance2[i][1])
                    distance.append(dist)
                res[temp] = distance
            
    return res

### newick file, get the reference gene blockres.add((temp,0))
'''@function: given a tree file, find the reference initial gene block 
   @input   : tree
   @output  : string (ref gene block)
'''   
def getRef(tree,ref):
    for node in tree.get_leaves():
        if ref in node.name:
            return node.gene_block
### newick file, storing info for each inner node about its cost so far, as well as computed a sample of sub optimal initial
'''@function: given a tree file, for each inner node, get the set of sub optimal value 
   @input   : tree
   @output  : tree
'''
def parseTree(tree):
    for node in tree.iter_descendants("postorder"):
        if not node.is_leaf():
            # create face contain initial set info
            node.sample = generateSample(node)
            print (node.sample)
    return tree
if __name__ == "__main__":

    args = get_arguments()
    tree = Tree(args.Operon)
    # get the gene block in reference genomes
    tree = parseTree(tree) 
    



