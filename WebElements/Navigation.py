#!/usr/bin/python
"""
   Name:
       Navigation Elements

   Description:
       Contains reusable WebElements that aid in page navigation.

"""

import Base
import Buttons
import Containers
import Display
import HiddenInputs
import Inputs
import Layout
import UITemplate
from Factory import Factory
from IteratorUtils import iterableLength
from MethodUtils import CallBack
from PositionController import PositionController
from StringUtils import interpretAsString

Factory = Factory(Base.Invalid, name="Navigation")


class ItemPager(Layout.Vertical):
    """
        Paged Results:
        Encapsulates the UI logic for paging multiple item from a database or other source.
    """
    signals = Base.TemplateElement.signals + ['jsIndexChanged']
    properties = Base.TemplateElement.properties.copy()
    properties['itemsPerPage'] = {'action':'classAttribute', 'type':'int'}
    properties['pagesShownAtOnce'] = {'action':'classAttribute', 'type':'int'}

    def __init__(self, id, name=None, parent=None):
        Layout.Vertical.__init__(self, id, name, parent)

        positionLayout = self.addChildElement(Layout.Horizontal())
        label = positionLayout.addChildElement(Display.Label())
        label.setText('Showing Results')
        label.addClass('Spaced Word')

        self.resultsStartAt = positionLayout.addChildElement(Display.Label())
        self.resultsStartAt.strong = True
        self.resultsStartAt.setText('1')
        self.resultsStartAt.addClass('SpacedWord')

        label = positionLayout.addChildElement(Display.Label())
        label.setText('-')
        label.addClass('Spaced Word')

        self.resultsEndAt = positionLayout.addChildElement(Display.Label())
        self.resultsEndAt.strong = True
        self.resultsEndAt.setText('25')
        self.resultsEndAt.addClass('SpacedWord')

        label = positionLayout.addChildElement(Display.Label())
        label.setText('out of')
        label.addClass('Spaced Word')

        self.numberOfResults = positionLayout.addChildElement(Display.Label())
        self.numberOfResults.strong = True
        self.numberOfResults.setText('100')
        self.numberOfResults.addClass('SpacedWord')

        self.showAllButton = positionLayout.addChildElement(Buttons.ToggleButton('showAllButton'))
        self.showAllButton.setText("Show All")

        buttonLayout = self.addChildElement(Layout.Horizontal())

        self.startButton = buttonLayout.addChildElement(Buttons.Link())
        self.startButton.setText("&lt;&lt;")
        self.startButton.setDestination("#Link")

        self.backButton = buttonLayout.addChildElement(Buttons.Link())
        self.backButton.setText("&lt; Back")
        self.backButton.setDestination("#Link")
        self.backButton.addClass("SpacedWord")

        self.pageLinks = buttonLayout.addChildElement(Layout.Flow())

        self.nextButton = buttonLayout.addChildElement(Buttons.Link())
        self.nextButton.setText("Next &gt;")
        self.nextButton.setDestination("#Link")

        self.lastButton = buttonLayout.addChildElement(Buttons.Link())
        self.lastButton.setText("&gt;&gt;")
        self.lastButton.setDestination("#Link")
        self.lastButton.addClass("SpacedWord")

        self.pagesShownAtOnce = 15
        self.itemsPerPage = 25
        self._index_ = self.addChildElement(HiddenInputs.HiddenIntValue(id + 'Index'))
        self._pages_ = None

        self.connect('beforeToHtml', None, self, '_updateUI_')
        self.showAllButton.addJavascriptEvent('onclick', "JUReplaceElement(this, JUBuildThrobber());")
        self.showAllButton.connect('jsToggled', None, self, 'jsSetNavigationIndex', 0)
        self.showAllButton.connect('toggled', True, self.showAllButton, 'setValue', 'Show in Pages')
        self.showAllButton.connect('toggled', False, self.showAllButton, 'setValue', 'Show All')

    def setItems(self, items=None):
        """
            Set a list of items for the item pager to page-through
        """
        itemsPerPage = int(self.itemsPerPage)
        if iterableLength(items) <= itemsPerPage:
            self.showAllButton.remove()
        elif self.showAllButton.toggled():
            itemsPerPage = iterableLength(items)

        self._pages_ = PositionController(items=items or [], startIndex=self._index_.value(),
                                          itemsPerPage=itemsPerPage,
                                          pagesShownAtOnce=int(self.pagesShownAtOnce))
        self._index_.setValue(self._pages_.startIndex)

    def currentPageItems(self):
        """
            The items contained in the currently highlighted page
        """
        return self._pages_.currentPageItems

    def jsSetNavigationIndex(self, index):
        """
            Creates the javascript to switch to a different position within the items:
            index - the first item you want to appear in your pages results
        """
        return ("JUGetElement('%(id)sIndex').value = '%(index)d';%(handlers)s;" %
                {'id':self.jsId(), 'index':index, 'handlers':"\n".join(self.emit('jsIndexChanged'))})

    def _updateUI_(self):
        """
            Updates the ui to reflect the currently selected page and provide links to other pages
        """
        if not self._pages_:
            return
        elif not self.currentPageItems():
            self.hide()
            return

        self.resultsStartAt.setText(self._pages_.startPosition)
        self.resultsEndAt.setText(self._pages_.nextPageIndex)
        self.numberOfResults.setText(self._pages_.length)

        if self._pages_.areMore:
            self.nextButton.show()
            self.lastButton.show()
            self.nextButton.addJavascriptEvent('onclick', self.jsSetNavigationIndex(self._pages_.nextPageIndex))
            self.lastButton.addJavascriptEvent('onclick', self.jsSetNavigationIndex(self._pages_.lastPageIndex))
        else:
            self.nextButton.hide()
            self.lastButton.hide()

        if self._pages_.arePrev:
            self.backButton.show()
            self.startButton.show()
            self.backButton.addJavascriptEvent('onclick', self.jsSetNavigationIndex(self._pages_.prevPageIndex))
            self.startButton.addJavascriptEvent('onclick', self.jsSetNavigationIndex(0))
        else:
            self.backButton.hide()
            self.startButton.hide()

        pageList = self._pages_.pageList()
        if len(pageList) > 1:
            for page in self._pages_.pageList():
                link = self.pageLinks.addChildElement(Buttons.Link())
                link.setText(unicode(page / self._pages_.itemsPerPage + 1))
                link.addClass('SpacedWord')
                if page != self._index_.value():
                    link.setDestination('#Link')
                    link.addJavascriptEvent('onclick', self.jsSetNavigationIndex(page))

Factory.addProduct(ItemPager)


class JumpToLetter(Layout.Vertical):
    """
        Provides a simple set of links that allow a user to jump to a particular letter
    """
    letters = map(chr, xrange(ord('A'), ord('Z') + 1))
    signals = Layout.Vertical.signals + ['jsLetterClicked']

    def __init__(self, id, name=None, parent=None):
        Layout.Vertical.__init__(self, id, name, parent)
        self.addClass("WJumpToLetter")
        self.style['float'] = "left"

        self.__letterMap__ = {}
        self.selectedLetter = self.addChildElement(HiddenInputs.HiddenValue(self.id + "SelectedLetter"))
        for letter in self.letters:
            link = self.addChildElement(Buttons.Link())
            link.addClass("WLetter")
            link.setText(letter)

            self.__letterMap__[letter] = link

        self.selectedLetter.connect('valueChanged', None, self, "selectLetter")

        self.connect("beforeToHtml", None, self, "__highlightSelectedLetter__")
        self.addScript("function letterJumpHover(letterJump){"
                       "    var letterJump = JUGetElement(letterJump);"
                       "    letterJump.paddingBottom = '4px';"
                       "    letterJump.paggingTop = '3px';"
                       "}")
        self.addScript("function letterJumpLeave(letterJump){"
                       "    var letterJump = JUGetElement(letterJump);"
                       "    letterJump.paddingBottom = '10px';"
                       "    letterJump.paggingTop = '10px';"
                       "}")

    def __highlightSelectedLetter__(self):
        jsId = self.jsId()
        functionName = jsId.replace(".", "").replace(":", "") + "SelectLetter"
        self.addScript(("function %s(letter){"
                        "    JUGetElement('%s').value = letter;"
                        "    %s"
                        "}") % (functionName, self.selectedLetter.jsId(), "\n".join(self.emit("jsLetterClicked"))))
        for letter, link in self.__letterMap__.iteritems():
            if letter == self.selectedLetter.value():
                link.addClass("WLetterSelected")
            else:
                link.setDestination("#" + letter)
                if not link.javascriptEvent('onmouseover'):
                    link.addJavascriptEvent("onmouseover", "letterJumpHover('%s');" % jsId)
                    link.addJavascriptEvent("onmouseout", "letterJumpLeave('%s')" % jsId)
                    link.addJavascriptEvent("onclick", "%s('%s');" % (functionName, letter))

    def clearSelection(self):
        """
            Deselects the currently selected letter (if there is one)
        """
        self.selectedLetter.setValue('')

    def selectLetter(self, letter):
        """
            Selects the passed in letter
        """
        self.selectedLetter.setValue(letter)

    def unselectLetter(self, letter):
        """
            Unselects the letter if it matches letter, otherwise does nothing
        """
        if letter == self.selectedLetter:
            self.selectedLetter.setValue('')

Factory.addProduct(JumpToLetter)


class BreadCrumb(Layout.Box):
    """
        Defines a dynamically built navigation breadcrumb
    """
    properties = Layout.Box.properties.copy()
    properties['formName'] = {'action':'classAttribute'}

    def __init__(self, id, name=None, parent=None):
        Layout.Box.__init__(self, id, name, parent)
        self.addClass("WBreadCrumb")

        hiddenData = Inputs.TextBox(id + ':HiddenData')
        hiddenData.attributes['type'] = 'hidden'
        self.hiddenData = self.addChildElement(hiddenData)

        prevLinkClicked = Inputs.TextBox(id + ':LinkClicked')
        prevLinkClicked.attributes['type'] = 'hidden'
        self.prevLinkClicked = self.addChildElement(prevLinkClicked)

        location = Inputs.TextBox(id + ':Location')
        location.attributes['type'] = 'hidden'
        self.location = self.addChildElement(location)

        label = Inputs.TextBox(id + ':Label')
        label.attributes['type'] = 'hidden'
        self.label = self.addChildElement(label)

        key = Inputs.TextBox(id + ':Key')
        key.attributes['type'] = 'hidden'
        self.key = self.addChildElement(key)

        self.currentLocation = ''
        self.currentText = ''
        self.formName = "setMe"

        self.linkCount = 0
        self.links = []
        self.addLink('Home', 'Home')

        self.addScript(CallBack(self, 'jsSubmitLink'))

        self.connect('beforeToHtml', None, self, 'highlightCurrentLink')

        self.trail = []

    def addLink(self, text, location, key=None):
        """
            Adds a link to the breadcumb that can be clicked to return to a previous location
        """
        key = key or text

        if self.currentLocation:
            self.trail.append({'field':self.currentLocation, 'term':key})

            spacer = Display.Label('spacer')
            spacer.addClass("BreadCrumbSpacer")
            spacer.setText(' >> ')
            self.addChildElement(spacer)

            value = self.hiddenData.value()
            if value:
                value += '[/]'
            value += text + '[:]' + location + '[:]' + key
            self.hiddenData.setValue(value)

        link = Buttons.Link('breadcrumb')
        link.addClass("BreadCrumbLink")
        link.setText(text)
        link.name = unicode(self.linkCount)
        link.addJavascriptEvent('onclick', "submitLink('" + text + "', '" +
                                                       location + "', '" +
                                                       key + "', '" +
                                                       unicode(self.linkCount) + "');")

        self.currentLocation = location
        self.currentText = text
        self.addChildElement(link)
        self.currentLink = link
        self.linkCount += 1
        self.links.append(link)
        return link

    def filterDict(self):
        """
            Returns a dictionary of field - term, to represent your current location based on the breadcrumbs
        """
        data = {}
        for location in self.trail:
            data[location['field']] = location['term']

        return data

    def jsSubmitLink(self):
        """
            Returns the javascript that will change your location in the breadcrumb trail clientside
        """
        return """
                function submitLink(label, view, key, index){
                    if(index != null){
                        link = JUGetElement('""" + self.prevLinkClicked.id + """');
                        link.value = index;
                    }
                    if(key == null){
                        key = label;
                    }

                    JUGetElement('""" + self.label.id  + """').value = label;
                    JUGetElement('""" + self.location.id + """').value = view;
                    JUGetElement('""" + self.key.id + """').value = key;
                    JUGetElement('""" + self.formName + """').submit();
                }
               """

    def highlightCurrentLink(self):
        """
            Updates the display of the current link to reflected its highlighted status
        """
        self.currentLink.removeClass('BreadCrumbLink')

    def insertVariables(self, valueDict=None):
        Layout.Box.insertVariables(self, valueDict)

        clicked = 'none'
        if self.prevLinkClicked.value():
            clicked = int(self.prevLinkClicked.value())

        links = self.hiddenData.value()
        self.hiddenData.setValue('')
        self.prevLinkClicked.setValue('')
        if clicked != 0:
            if links:
                current = 1
                for link in links.split('[/]'):
                    if current == clicked:
                        break

                    label, location, key = link.split('[:]')
                    self.addLink(label, location, key)

                    current += 1

            if self.location.value():
                self.addLink(self.label.value(),
                             self.location.value(),
                             self.key.value())
                self.location.setValue('')
                self.label.setValue('')
                self.key.setValue('')

Factory.addProduct(BreadCrumb)


class UnrolledSelect(Display.List):
    """
         A select input implementation where all options are visible at once but only one is selectable
    """
    def __init__(self, id, name=None, parent=None):
        Display.List.__init__(self, None, None, parent)
        self.addChildElement(Display.Label()).addClass('first')
        self.addClass('WUnrolledSelect')
        self.userInput = HiddenInputs.HiddenValue(id, parent=self)
        self.childElements.append(self.userInput)
        self.userInput.addClass("Value")
        self.options = []

        self.addScript("function selectUnrolledOption(option)"
                       "{"
                       "    var valueElement = JUFellowChild(option, 'WUnrolledSelect', 'Value');"
                       "    valueElement.value = option.name;"
                       "    valueElement.onchange();"
                       "    JUStealClassFromFellowChild(option, 'WUnrolledSelect', 'selected');"
                       "}")

        self.connect('beforeToHtml', None, self, '__addLast__')

    def __addLast__(self):
        self.addChildElement(Display.Label()).addClass('last')
        self.disconnect('beforeToHtml', None, self, '__addLast__')

    def addOptions(self, options, displayKeys=False):
        """
            Adds a group of options to a select box:

            options - Takes a dictonary of option keys to option values
                      or a straight list of option names

            displayKeys(False) - if dictionaries keys will be used for display and the values
                                 will be used for keys
        """
        if isinstance(options, dict):
            for key, value in options.iteritems():
                self.addOption(key, value, displayKeys)
        else:
            for option in options:
                self.addOption(option)

    def addOptionList(self, options, displayKeys=True):
        """
            Adds a options based on a list of tuple(name-value) pairs
        """
        for option in options:
            name = option['name']
            value = option['value']
            self.addOption(name, value, displayKeys)

    def addOption(self, key, value=None, displayKeys=True):
        """
            Adds a new option that can be selected
        """
        newOption = Buttons.Link()
        newOption.setDestination("#Link")
        if not self.options:
            newOption.addClass('selected')
        if not value:
            value = key

        key = interpretAsString(key)
        value = interpretAsString(value)
        if displayKeys:
            newOption.name = value
            newOption.setText(key)
        else:
            newOption.name = key
            newOption.setText(value)

        newOption.addJavascriptEvent('onclick', 'selectUnrolledOption(this);')

        self.options.append(newOption)
        return self.addChildElement(newOption)

    def options(self):
        """
            Returns a list of all available options
        """
        options = {}
        for option in self.options:
            options[option.name] = option.text()

        return options

    def selected(self):
        """
            Returns the selected item
        """
        for option in self.childElements:
            if option.selected():
                return option

    def setValue(self, value):
        """
            Selects a child select option
        """
        for option in self.options:
            if option.name == "value":
                option.addClass('selected')
            else:
                option.removeClass('selected')

    def value(self):
        """
            Returns the value of the currently selected item
        """
        for option in self.options:
            if option.hasClass('selected'):
                return option.name

Factory.addProduct(UnrolledSelect)


class TimeFrame(Layout.Horizontal):
    """
        Allows a user to select the time frame from which items will appear
    """
    signals = Base.TemplateElement.signals + ['jsTimeFrameChanged']
    properties = Layout.Horizontal.properties.copy()
    properties['help'] = {'action':'help.setText'}
    properties['disableAnyTime'] = {'action':'call', 'type':'bool'}

    def __init__(self, id, name=None, parent=None):
        Layout.Horizontal.__init__(self, id, name, parent)
        self.style['margin-top'] = '2px'
        self.addClass("WTimeFrame")

        label = self.addChildElement(Display.Label())
        label.setText('Show Timeframe:')
        label.addClass("TimeFrameLabel")

        self.anyTime = self.addChildElement(Buttons.Link())
        self.anyTime.addClass('SpacedWord')
        self.anyTime.setText('All,')

        self.hours24 = self.addChildElement(Buttons.Link())
        self.hours24.addClass('SpacedWord')
        self.hours24.setText('24 Hours,')

        self.days7 = self.addChildElement(Buttons.Link())
        self.days7.addClass('SpacedWord')
        self.days7.setText('7 Days,')

        self.days14 = self.addChildElement(Buttons.Link())
        self.days14.addClass('SpacedWord')
        self.days14.setText('14 Days')

        self.helpDropDown = self.addChildElement(Containers.DropDownMenu('help'))
        helpLink = self.helpDropDown.addChildElement(Buttons.Link())
        helpLink.setText("(Describe Time Frame)")
        helpLink.setDestination("#Link")
        self.help = self.helpDropDown.addChildElement(Display.Label())
        self.help.setText("Help text goes here")

        self.days = self.addChildElement(HiddenInputs.HiddenIntValue(id + ":days"))
        self.days.addClass('Value')
        self.connect('beforeToHtml', None, self, '__addScripts__')

    def disableAnyTime(self):
        """
            Will display the anyTime option in addition to the 14 days, 7 days and 1 day options
        """
        self.anyTime.remove()
        if self.days.value() == 0:
            self.days.setValue(1)

    def __addScripts__(self):
        setTimeFrame = ("JUStealClassFromPeer(this, 'selected');JUPeer(this, 'Value').value = '%d';" +
                        "".join(self.emit("jsTimeFrameChanged")))
        valueMap = {0:self.anyTime, 1:self.hours24, 7:self.days7, 14:self.days14}
        for value, element in valueMap.iteritems():
            element.addJavascriptEvent('onclick', setTimeFrame % value)
        valueMap[self.days.value()].addClass('selected')

Factory.addProduct(TimeFrame)
