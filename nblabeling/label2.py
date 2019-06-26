
try:
    import ipywidgets as widgets
    from ipywidgets import Button, HBox, VBox, interact, IntSlider
    has_ipywidgets = True
except:
    has_ipywidgets = False

try:
    from IPython.display import display, clear_output
    has_ipy = True
except:
    has_ipy = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.colors import LinearSegmentedColormap
    has_plt = True
except:
    has_plt = False

import numpy as np




class Labelizer():
    def __init__(self, img_array_lst):
        """
          Labelizer will page through image/labels and allow users to remove/change data or labels from a VedaBase or VedaStream
          Params:
            vset: The data to be cleaned
            mltype: the type of ML data. Can be 'classification' 'segmentation' or 'object_detection'
            count: the number of datapoints to iterate through
            classes: the classes in the dataset
        """
        assert has_ipywidgets, 'Labelizer requires ipywidgets to be installed'
        assert has_ipy, 'Labelizer requires ipython to be installed'
        assert has_plt, 'Labelizer requires matplotlib to be installed'

        self.img_array_list = img_array_lst
        self.count = len(img_array_lst)


        self.index = None
        self.flagged_tiles = []
        self.iflagged_tiles = []
        self._get_next()  #create images, labels, and datapoint


    def _get_next(self):
        if self.index is not None:
            self.index +=1
        else:
            self.index = 0
        self.datapoint = self.img_array_list[self.index] ###get next item in index
        

    # def _create_images(self):
    #     """
    #     Creates image tiles from a datapoint
    #     returns:
    #         img: An image tile of size (M,N,3)
    #     """
    #     if isinstance(self.vedaset, veda.api.VedaCollectionProxy):
    #         img = self.datapoint.image
    #     elif isinstance(self.vedaset, (stream.vedastream.BufferedSampleArray,
    #                   store.vedabase.H5SampleArray)):
    #         img = np.moveaxis(self.datapoint[0], 0, -1)
    #     return img

    # def _create_labels(self):
    #     """
    #     Generates labels for a datapoint's image tile
    #     returns:
    #         labels: a list of labels for an image tile
    #     """
    #     if isinstance(self.vedaset, veda.api.VedaCollectionProxy):
    #         labels = self.datapoint.label.values()
    #     elif isinstance(self.vedaset, (stream.vedastream.BufferedSampleArray,
    #                   store.vedabase.H5SampleArray)):
    #         labels = self.datapoint[1]
    #     return labels

    def _create_buttons(self):
        """
        Creates ipywidget widget buttons
        Returns:
            buttons: A list of ipywidget Button() objects
        """
        buttons = []
        actions = [('Yes', 'success'), ('No', 'danger'), ('Exit', 'info')]
        for b in actions:
            btn = Button(description=b[0], button_style=b[1])
            buttons.append(btn)
        return buttons


    def _handle_buttons(self, b):
        """
        Callback and handling of widget buttons.
        """
        if b.description == 'Yes':
            self._get_next()
        elif b.description == 'No':
            self.flagged_tiles.append(self.datapoint)
            self._get_next()
        elif b.description == 'Exit':
            self.index = self.count
        self.clean()



    def _recolor_images(self):
        img = self.image.astype('float32')
        img[:,:,0] /= np.max(img[:,:,0])
        img[:,:,1] /= np.max(img[:,:,1])
        img[:,:,2] /= np.max(img[:,:,2])
        return(img)

    def _display_image(self):
        """
        Displays image tile for a given vedaset object.
        """
        if self.image.dtype == 'uint16':
            img = self._recolor_images()
        else:
            img = self.image
        plt.figure(figsize = (10, 10))
        self.ax = plt.subplot()
        self.ax.axis("off")
        self.ax.imshow(img)



    def _display_classification(self, title=True):
        """
        Adds vedaset classification labels to the image plot.
        """
        if title:
            plt.title('Does this tile contains matching imagery', fontsize=14)
        else:
            plt.title('Tile contains: no labeled objects', fontsize=14)

    def clean(self):
        """
        Method for verifying each vedaset object as image data with associated polygons.
        Displays a polygon overlayed on image chip with associated ipywidget
        buttons. Allows user to click through each vedaset object and decide
        whether to keep or remove the object.
        """
        clear_output()
        buttons = self._create_buttons()
        for b in buttons:
            b.on_click(self._handle_buttons)
        if self.image is not None and self.index != self.count:
            print("%0.f tiles out of %0.f tiles have been cleaned" %
                  (self.index, self.count))
            display(HBox(buttons))
            self._display_image()
            self._display_classification()

        else:
            try:
                print("You've flagged %0.f bad tiles. Review them now" % len(self.flagged_tiles))
                self.iflagged_tiles = iter(self.flagged_tiles)
                self.image = self._create_images()
                self.labels = self._create_labels()
                self.clean_flags()
            except StopIteration:
                print("All tiles have been cleaned.")