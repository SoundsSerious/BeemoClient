from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.actionbar import ActionBar
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from beem import *
from log import BufferLog

from kivy.lang import Builder
Builder.load_string('''
<BeemoBar@ActionBar>:
    pos_hint: {'top':1}
    ActionView:
        use_separator: True
        ActionButton:
            text: 'Btn0'
            icon: 'images/Beemo_CircleOnly_fav.png'
        ActionPrevious:
            title: 'Action Bar'
            with_previous: False
        ActionOverflow:

        ActionButton:
            text: 'Btn1'
        ActionButton:
            text: 'Btn2'
        ActionButton:
            text: 'Btn3'
        ActionButton:
            text: 'Btn4'
        ActionGroup:
            text: 'Group1'
            ActionButton:
                text: 'Btn5'
            ActionButton:
                text: 'Btn6'
            ActionButton:
                text: 'Btn7'
''')
    
class BeemoBar(ActionBar):
    pass
 
class BeemoApp(App):

    _client = None    
    
    def build(self):
        lay = BoxLayout(orientation = 'vertical')
        
        ab = BeemoBar()
        tb_panel= TabbedPanel()
        
        lay.add_widget(ab)
        lay.add_widget(tb_panel)
        
        self.onButton = Button(text = 'ON')
        self.onButton.bind( on_press = self.call_on)
        
        self.offButton = Button(text = 'OFF')
        self.offButton.bind( on_press = self.call_off)
        
        powerWidget = BoxLayout(orientation = 'vertical')
        powerWidget.add_widget( self.onButton )
        powerWidget.add_widget( self.offButton )
        
        #Create text tab          
        th_text_head = TabbedPanelHeader(text='Power')
        th_text_head.content= powerWidget
        
        #Create image tab
        th_img_head= TabbedPanelHeader(text='Color')
        th_img_head.content= Image(source='images/Beemo_CircleOnly_Med.png',pos=(400, 100), size=(400, 400))
         
        #Create button tab
        th_log = TabbedPanelHeader(text='Info')
        self._log = BufferLog(self, 200)
        self._log.addText( 'hello beeche ')
        th_log.content = self._log
        
        tb_panel.add_widget(th_text_head)
        tb_panel.add_widget(th_img_head)
        tb_panel.add_widget(th_log)          
        
        Clock.schedule_once(self.start_netService)
        return lay
        
    def on_connection(self, client):
        self.log("connected succesfully!")
        self._client = client
        
    def log(self, text):
        '''Call Back From BEEM'''
        #We add text to BufferLog
        self._log.addText( text )
        
    def sendCommand(self,primaryKey,secondaryKey,argument=''):
        if self._client:
            msg = '{} {} {}'.format( primaryKey, secondaryKey, argument)
            self._client.sendLine(msg)
            
    def call_on(self,instance):
        self.sendCommand('PWR','ONN')

    def call_off(self,instance):
        self.sendCommand('PWR','OFF')
        
    def start_netService(self,dt):
        #Call back cus argument
        self.setupNetworkServices()
          
    def setupNetworkServices(self):
        self.log( "starting rectors capin\'")
        reactor.connectTCP(HOST, PORT, BeemoClient( self ))
        
        self.log('Starting MDNS Name Service')
        d = broadcast(reactor, "_beem._tcp", PORT+1, "beemo_dev")
        d.addCallback(broadcasting)
        d.addErrback(failed)
 
if __name__ == '__main__':
    BeemoApp().run()