import Base
import Factory
from Display import Image

Factory = Factory.Factory(Base.Invalid, name="Charts")


class GoogleChart(Image):
    """
        Provides a way for the google chart api to be used via WebElements
    """
    chartType = None
    url = ('http://chart.apis.google.com/chart?cht='
           '%(chart)s&chs=%(width)sx%(height)s&chd=t:%(data)s&chl=%(labels)s&chbh=a'
           '&chxt=y&chds=0,%(max)f&chxr=0,0,%(max)f&chco=4D89F9')
    properties = Base.WebElement.properties.copy()
    properties['height'] = {'action':'setHeight', 'type':'int'}
    properties['width'] = {'action':'setWidth', 'type':'int'}

    def __init__(self, id=None, name=None, parent=None):
        super(GoogleChart, self).__init__(id, name, parent)
        self.__dataPoints__ = {}
        self.__height__ = 100
        self.__width__ = 100

        self.connect("beforeToHtml", None, self, "__updateSource__")

    def setWidth(self, width):
        """
            Set the width of the google chart in pixels (maximum allowed by google is 1000 pixels)
        """
        width = int(width)
        if width > 1000:
            raise ValueError("Google charts has a maximum width limit of 1000 pixels")
        self.__width__ = width

    def width(self):
        """
            Returns the set width of the google chart in pixels
        """
        return self.__width__

    def setHeight(self, height):
        """
            Set the height of the google chart in pixels (maximum allowed by google is 1000 pixels)
        """
        height = int(height)
        if height > 1000:
            raise ValueError("Google charts has a maximum height limit of 1000 pixels")
        self.__height__ = height

    def height(self):
        """
            Returns the set height of the google chart in pixels
        """
        return self.__height__

    def addData(self, label, value):
        """
            Adds a data point to the chart,
                  label: the label to associate with the data point
                  value: the numeric value of the data
        """
        self.__dataPoints__[str(label)] = value

    def __updateSource__(self):
        data = self.__dataPoints__ or {'No Data!':'100'}
        self.style['width'] = self.__width__

        items = []
        for key, value in data.iteritems():
            items.append((value, key))
        items.sort()
        keys = [key for value, key in items]
        values = [value for value, key in items]

        self.style['height'] = self.__height__
        self.setValue(self.getURL(keys, values))

    def getURL(self, keys, values):
        """
            Returns the google chart url based on the data points given
        """
        return self.url % {'chart':self.chartType, 'width':str(self.__width__),
                           'height':str(self.__height__),
                           'data':",".join([str(value) for value in values]),
                           'labels':"|".join(keys),
                           'max':float(max(values)),
                           }


class PieChart(GoogleChart):
    """
        Implementation of Google's pie chart
    """
    chartType = "p"

Factory.addProduct(PieChart)


class PieChart3D(GoogleChart):
    """
        Implementation of Google's 3d pie chart
    """
    chartType = "p3"

Factory.addProduct(PieChart3D)


class HorizontalBarChart(GoogleChart):
    """
        Implementation of Googles Horizontal Bar Chart
    """
    chartType = "bhs"
    url = ('http://chart.apis.google.com/chart?cht='
           '%(chart)s&chs=%(width)sx%(height)s&chd=t:%(data)s&chxl=1:|%(labels)s&chbh=a'
           '&chxt=x,y&chds=0,%(max)f&chxr=0,0,%(max)f&chco=4D89F9')

    def getURL(self, keys, values):
        """
            Returns the google chart url based on the data points given
        """
        return self.url % {'chart':self.chartType, 'width':str(self.__width__),
                           'height':str(self.__height__),
                           'data':",".join([str(value) for value in values]),
                           'labels':"|".join(reversed(keys)),
                           'max':float(max(values)),
                           }

Factory.addProduct(HorizontalBarChart)


class VerticalBarChart(GoogleChart):
    """
        Implementation of Google's Vertical Bar Chart
    """
    chartType = "bvs"

Factory.addProduct(VerticalBarChart)


class LineChart(GoogleChart):
    """
        Implementation of Google's Line Chart
    """
    chartType = "lc"

Factory.addProduct(LineChart)
