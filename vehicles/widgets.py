from django import forms


class MapWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        return '<div id="map"></div>'
    
    