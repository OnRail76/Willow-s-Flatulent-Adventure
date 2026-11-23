import sys, time
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from sms import SMS, UP, DOWN, LEFT, RIGHT, B1, B2
def load():
    return SMS(open(os.path.join(ROOT, 'build', 'willow.sms'),'rb').read())
def syms():
    d={}
    for l in open(os.path.join(ROOT, 'build', 'willow.sym')):
        a,n=l.split(); d[n]=int(a,16)
    return d
