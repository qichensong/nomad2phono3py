import matplotlib.pyplot as plt
import matplotlib.image as mpimg
img = mpimg.imread('lifetime.png')
imgplot = plt.imshow(img)
plt.axis('off')
plt.show()
