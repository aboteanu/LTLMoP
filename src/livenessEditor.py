#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.4 on Thu Jan  9 01:50:11 2014

import wx, wx.richtext, wx.stc

# begin wxGlade: extracode
# end wxGlade


class AnalysisResultsDialog(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        # begin wxGlade: AnalysisResultsDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_traceback = wx.StaticText(self, -1, "Specification:")
        self.tree_ctrl_traceback = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS | wx.TR_NO_LINES | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HIDE_ROOT | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)
        self.label_3 = wx.StaticText(self, -1, "Analysis Output:")
        self.text_ctrl_summary = wx.richtext.RichTextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.label_1 = wx.StaticText(self, -1, "Enter new environment liveness:")
        self.text_ctrl_1 = wx.richtext.RichTextCtrl(self, -1, "")
        self.button_refine = wx.Button(self, -1, "Resynthesize")
        self.button_1 = wx.Button(self, wx.ID_CLOSE, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onClickResynthesize, self.button_refine)
        self.Bind(wx.EVT_BUTTON, self.onButtonClose, self.button_1)
        # end wxGlade
        
        self.parent = parent

    def __set_properties(self):
        # begin wxGlade: AnalysisResultsDialog.__set_properties
        self.SetTitle("Analysis Results")
        self.SetSize((562, 602))
        self.label_traceback.Hide()
        self.tree_ctrl_traceback.Hide()
        self.text_ctrl_1.SetMinSize((430, 35))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: AnalysisResultsDialog.__do_layout
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11.Add(self.label_traceback, 0, wx.ALL, 5)
        sizer_11.Add(self.tree_ctrl_traceback, 3, wx.ALL | wx.EXPAND, 5)
        sizer_11.Add(self.label_3, 0, wx.ALL, 5)
        sizer_11.Add(self.text_ctrl_summary, 1, wx.ALL | wx.EXPAND, 5)
        sizer_11.Add(self.label_1, 0, wx.ALL, 5)
        sizer_1.Add(self.text_ctrl_1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(self.button_refine, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_11.Add(sizer_1, 0, wx.EXPAND, 45)
        sizer_16.Add((20, 20), 1, wx.EXPAND, 0)
        sizer_16.Add(self.button_1, 0, wx.ALL | wx.EXPAND, 5)
        sizer_11.Add(sizer_16, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_11)
        self.Layout()
        # end wxGlade

    def onClickResynthesize(self, event):  # wxGlade: AnalysisResultsDialog.<event_handler>
        self.parent.onMenuResynthesize(self.text_ctrl_1.GetLineText(0)) #lineNo    
        event.Skip()

    def onButtonClose(self, event):  # wxGlade: AnalysisResultsDialog.<event_handler>
        self.Hide()
        event.Skip()
        
    def appendLog(self, text, color="BLACK"):
        self.text_ctrl_summary.BeginTextColour(color)
        self.text_ctrl_summary.WriteText(text)
        self.text_ctrl_summary.EndTextColour()
        self.text_ctrl_summary.ShowPosition(self.text_ctrl_summary.GetLastPosition())
        wx.Yield() # Ensure update
        

    def populateTreeStructured(self, structuredSpec, LTL2SpecLineNumber, tracebackTree, ltlSpec , to_highlight , normalEnvSafetyCNF):
        """
        print the tree in tree_ctrl_traceback box
        structuredSpec: each line of spec in structured English in type LIST
        LTL2SpecLineNumber: dict for mapping bt structured English and LTL
        tracebackTree        : dict to access ['SysTrans'] and ['EnvTrans'] line number in EngSpec
        ltlSpec              : modified version of the ltl spec. going to print ['EnvTrans']
        to_highlight         : return from analysis that the specs with problems
        normalEnvSafetyCNF   : ltl env safety assumptions from ENV spec Generation
        """
        
        self.tree_ctrl_traceback.DeleteAllItems()
        root_node = self.tree_ctrl_traceback.AddRoot("Root")
        LTL  = {}
        for key,value in LTL2SpecLineNumber.iteritems():
            LTL[ value ] = key.replace('\t','').replace('\n','')
            #print key, value
        
        # highlight guilty specs
        highlightColor = "#FF9900"
        guilty_key = {}
        for h_item in to_highlight:
            if h_item[1] == 'goals':
                guilty_key[h_item[0].title() + h_item[1].title()] = h_item[2]
            else:
                guilty_key[h_item[0].title() + h_item[1].title()] = None
        
        hightlightEnvTrans = False
        guiltyLinesToHighlight = []
        for specType in guilty_key.keys():
            if specType == 'EnvTrans':
                hightlightEnvTrans = True
            elif specType == ('EnvGoals' or 'SysGoals'):
                guiltyLinesToHighlight.append(guilty_key[specType])
            else:
                for x in tracebackTree[specType]:
                    guiltyLinesToHighlight.append(x)
        
        
        for lineNo, EngSpec in enumerate(structuredSpec, start=1):
            # Build the traceback tree           
            if lineNo in tracebackTree['EnvTrans']: 
                # Add a node for each input line    
                input_node = self.tree_ctrl_traceback.AppendItem(root_node, EngSpec + "<--(REPLACED)") 
                 # white out original env transition spec 
                self.tree_ctrl_traceback.SetItemTextColour(input_node,"#a9a8a8")  
                #self.tree_ctrl_traceback.SetItemBackgroundColour(input_node,"#FA58D0") # pale pink
            else:
                # Add a node for each input line    
                input_node = self.tree_ctrl_traceback.AppendItem(root_node, EngSpec) 
                
            # add LTL as formula under the structured English if it exists   
            try:             
                command_node = self.tree_ctrl_traceback.AppendItem(input_node, LTL[ lineNo ])
                if lineNo in tracebackTree['EnvTrans']: 
                    self.tree_ctrl_traceback.SetItemTextColour(command_node,"#a9a8a8") 
            except:
                pass
                
            # hightlight guilty specs
            if lineNo in guiltyLinesToHighlight:
                self.tree_ctrl_traceback.SetItemBackgroundColour(input_node,highlightColor) # pale pink
                self.tree_ctrl_traceback.SetItemBackgroundColour(command_node,highlightColor) # pale pink
            
        # add the latest assumption generation here
        input_node = self.tree_ctrl_traceback.AppendItem(root_node, "NEWLY GENERATED ENV SAFETY ASSUMPTIONS") 
        #command_node = self.tree_ctrl_traceback.AppendItem(input_node, ltlSpec['EnvTrans'].replace('\t','').replace('\n','')) 
        for x in normalEnvSafetyCNF:
            command_node = self.tree_ctrl_traceback.AppendItem(input_node, x) 
        
        # highlight guilty specs
        if hightlightEnvTrans == True:
            self.tree_ctrl_traceback.SetItemBackgroundColour(input_node,highlightColor) # pale pink
            self.tree_ctrl_traceback.SetItemBackgroundColour(command_node,highlightColor) # pale pink
                        
        self.Layout()
 
    
    

# end of class AnalysisResultsDialog
if __name__ == "__main__":
    LivenessEditor = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    analysisResultsDialog = AnalysisResultsDialog(None, -1, "")
    LivenessEditor.SetTopWindow(analysisResultsDialog)
    analysisResultsDialog.Show()
    LivenessEditor.MainLoop()
