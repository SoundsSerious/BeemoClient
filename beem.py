# -*- coding: utf-8 -*-
"""
Created on Tue May 17 19:07:57 2016

@author: Sup
"""

"""
BEEMO: TWISTED DEV SERVER
"""
import os,sys

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.defer import Deferred
from twisted.python import log

import pybonjour
from twisted.internet.interfaces import IReadDescriptor
from zope import interface

PORT = 18330
HOST = 'frisbeem.local'
sdref = None

def broadcast(reactor, regtype, port, name=None):
    def _callback(sdref, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            d.callback((sdref, name, regtype, domain))
        else:
            d.errback(errorCode)

    d = Deferred()
    sdref = pybonjour.DNSServiceRegister(name = name,
                                        regtype = regtype,
                                        port = port,
                                        callBack = _callback)

    reactor.addReader(MDNS_ServiceDescriptor(sdref))
    return d
    

def broadcasting(args):
    global sdref
    sdref  = args[0]
    log.msg('Broadcasting %s.%s%s' % args[1:])

def failed(errorCode):
    log.err(errorCode)

class MDNS_ServiceDescriptor(object):

    interface.implements(IReadDescriptor)

    def __init__(self, sdref):
        self.sdref = sdref

    def doRead(self):
        pybonjour.DNSServiceProcessResult(self.sdref)

    def fileno(self):
        return self.sdref.fileno()

    def logPrefix(self):
        return "bonjour"

    def connectionLost(self, reason):
        self.sdref.close()
        

class Beem(LineReceiver):
    
    def __init__(self, factory):
        self.factory = factory
    
    def connectionMade(self):
        self.factory.app.log( 'Connection Made Sending Resp.' )
        self.sendLine("What's your name?")
        
    def lineReceived(self, line):
        self.factory.app.log( line )

class BeemoClient(ReconnectingClientFactory):
    protocol = Beem
    
    _callback = None
    def __init__(self, kivy_app):
        self.app = kivy_app

    def startedConnecting(self, connector):
        self.app.log('Started to connect.')

    def buildProtocol(self, addr):
        self.app.log( 'Connected.')
        self.app.log('Resetting reconnection delay')
        self.resetDelay()
        self.app.log('Connected from {}'.format(addr) )        
        return self.protocol(self)

    def clientConnectionLost(self, connector, reason):
        self.app.log('Lost connection.  Reason:' + str(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        #connector.connect()

    def clientConnectionFailed(self, connector, reason):
        self.app.log('Connection failed. Reason:' + str(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector,reason)
        #connector.connect()
        