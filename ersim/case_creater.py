from Tkinter import *
from PIL import Image, ImageTk

class App:
	def __init__(self, master):
		def callback(event):
			print str(event.x) + "," + str(event.y)

		tmp_image = Image.open("../Images/ros and pe/ros.png")
		imagetk = ImageTk.PhotoImage(tmp_image)

		label = Label(image=imagetk)
		label.image = imagetk
		label.bind("<Button-1>", callback)
		label.pack()


if __name__ == "__main__":
	root = Tk()
	app = App(root)
	root.mainloop()