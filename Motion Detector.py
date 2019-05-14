import cv2, time
import pandas as pd
from datetime import datetime

first_frame = None
video = cv2.VideoCapture(0)

while True:
	check, frame = video.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray,(21,21),0)

	if first_frame is None:
		first_frame = gray
		continue

	delta_frame = cv2.absdiff(first_frame,gray)
	thresh_delta = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
	thresh_delta = cv2.dilate(thresh_delta, None, iterations = 0)
	(_,cnts,_) = cv2.findContours(thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	for contour in cnts:
		if cv2.contourArea(contour) < 10000:
			continue
		(x,y,w,h) = cv2.boundingRect(contour)
		cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

	cv2.imshow('Frame',frame)
	cv2.imshow('gray',gray)
	cv2.imshow('delta_frame',delta_frame)
	cv2.imshow('thresh_frame',thresh_delta)

	key = cv2.waitKey(1)
	if key == ord('q'):
		break

video.release()
cv2.destroyAllWindows()

#Storing Time Values

status_list = [None,None]
times = []
df = pd.DataFrame(columns=["Start","End"])

video = cv2.VideoCapture(0)

while True:
	check, frame = video.read()
	status = 0
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray,(21,21),0)
	(_,cnts,_) = cv2.findContours(thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	for contour in cnts:
		if cv2.contourArea(contour) < 10000:
			continue
		status = 1
		(x,y,w,h) = cv2.boundingRect(contour)
		cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

	status_list.append(status)
	status_list = status_list[-2:]
	if status_list[-1] == 1 and status_list[-2] == 0:
		times.append(datetime.now())
	if status_list[-1] == 0 and status_list[-2] == 1:
		times.append(datetime.now())

	#print(status_list)
	#print(times)

	for i in range(0, len(times), 2):
		df = df.append({"Start" : times[i], "End" : times[i+1]}, ignore_index = True)

	df.to_csv("Times.csv", sep='\t', encoding='utf-8')

video.release()
cv2.destroyAllWindows()

from motion_detector import df
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumDataSource

df["Start_string"] = df["Start"].df.strftime("%Y-%m-%d %H:%M:%S")
df["End_string"] = df["End"].df.strftime("%Y-%m-%d %H:%M:%S")

cds = ColumnDataSource(df)

p = figure(x_axis_type = 'datatime', height = 100, width = 500, responsive = True, title = "Motion Graph")
p.yaxis.minor_tick_line_color = None
p.ygrid[0].ticker.desired_num_ticks = 1

hover = HoverTool(tooltips=[("Start","@Start_string"),("End","@End_string")])
p.add_tools(hover)

q = p.quad(left = "Start", right = "End", bottom = 0, top = 1, color="red", source = cds)

output_file("Graph.html")
show(p)