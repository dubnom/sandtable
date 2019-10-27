# flake8: noqa

from __future__ import division
from __future__ import print_function
from cam import *
from tkinter.filedialog import *
from tkinter import *
from past.utils import old_div
from builtins import range
from builtins import str
from future import standard_library
standard_library.install_aliases()
prompt = \
    """modes: 1D path following, 2D contour and raster, 3D slicing
input:
   *.svg: SVG (polylines and paths)
   *.dxf: DXF (2D polylines, 3D polymeshes)
   *.stl: STL (binary and ASCII)
   *.cmp,*.sol,*.via,*.mill: Gerber
      RS-274X format, with 0-width trace defining board boundary
   *.drl, *.drd: Excellon (with embedded drill defitions)
   *.jpg: z bitmap
output:
   *.rml: Roland Modela RML mill
   *.camm: Roland CAMM cutter
   *.jpg,*.bmp: images
   *.epi: Epilog lasercutter
   *.uni: Universal lasercutter
   *.g: G codes
   *.ord: OMAX waterjet cutter
   *.oms: Resonetics excimer micromachining center
   *.dxf: DXF
   *.stl: STL
keys: Q to quit
usage: python cam.py [[-i] infile][-d display scale][-p part scale][-x xmin][-y ymin][-o outfile][-f force][-v velocity][-t tooldia][-a rate][-e power][-s speed][-h height][-c contour][-r raster][-n no noise][-# number of arc segments][-j jobname][-w write toolpath]
"""


def plot(event):
    global vertices, faces, boundarys, toolpaths, \
        xmin, xmax, ymin, ymax, zmin, zmax
    #
    # scale and plot object and toolpath
    #
    print("plotting")
    xysize = float(sxysize.get())
    zsize = float(szsize.get())
    xyscale = float(sxyscale.get())
    zscale = float(szscale.get())
    xoff = float(sxmin.get()) - xmin*xyscale
    yoff = float(symin.get()) - ymin*xyscale
    zoff = float(szmax.get()) - zmax*zscale
    sdxy.set("  dx:%6.3f  dy:%6.3f" % ((xmax-xmin)*xyscale, (ymax-ymin)*xyscale))
    sdz.set("  dz:%6.3f" % ((zmax-zmin)*zscale))
    vert = ivert.get()
    if (len(boundarys) == 1):
        #
        # 2D plot
        #
        c.delete("plot_boundary")
        c.delete("plot_path")
        #
        # set scrollbars
        #
        xscrollmin = old_div((xmin*xyscale + xoff)*WINDOW, xysize)
        if (xscrollmin > 0):
            xscrollmin = 0
        xscrollmax = old_div((xmax*xyscale + xoff)*WINDOW, xysize)
        if (xscrollmax < WINDOW):
            xscrollmax = WINDOW
        yscrollmin = WINDOW - old_div((ymax*xyscale + yoff)*WINDOW, xysize)
        if (yscrollmin > 0):
            yscrollmin = 0
        yscrollmax = WINDOW - old_div((ymin*xyscale + yoff)*WINDOW, xysize)
        if (yscrollmax < WINDOW):
            yscrollmax = WINDOW
        c.configure(scrollregion=(xscrollmin, yscrollmin, xscrollmax, yscrollmax))
        if (xscrollmin == 0) & (xscrollmax == WINDOW):
            xscrollbar.grid_forget()
        else:
            xscrollbar.grid(row=1, column=0, sticky=E+W)
        if (yscrollmin == 0) & (yscrollmax == WINDOW):
            yscrollbar.grid_forget()
        else:
            yscrollbar.grid(row=0, column=1, sticky=N+S)
        #
        # mark origin
        #
        c.create_line([(old_div(-WINDOW, 20), WINDOW-1), (old_div(WINDOW, 20), WINDOW-1)], fill="blue")
        c.create_line([(0, WINDOW+old_div(WINDOW, 20)), (0, WINDOW-old_div(WINDOW, 20))], fill="blue")
        #
        # plot boundary segments
        #
        for seg in range(len(boundarys[0])):
            path_plot = []
            for vertex in range(len(boundarys[0][seg])):
                xplot = int(old_div((boundarys[0][seg][vertex][X]*xyscale + xoff)*WINDOW, xysize))
                path_plot.append(xplot)
                yplot = (WINDOW-1) - int(old_div((boundarys[0][seg][vertex][Y]*xyscale + yoff)*WINDOW, xysize))
                path_plot.append(yplot)
                if (vert == 1):
                    c.create_text(xplot, yplot, text=str(seg)+':'+str(vertex), tag="plot_boundary")
            c.create_line(path_plot, tag="plot_boundary")
        c.delete("plot_path")
        #
        # plot toolpath segments
        #
        for seg in range(len(toolpaths[0])):
            path_plot = []
            for vertex in range(len(toolpaths[0][seg])):
                xplot = int(old_div((toolpaths[0][seg][vertex][X]*xyscale + xoff)*WINDOW, xysize))
                path_plot.append(xplot)
                yplot = (WINDOW-1) - int(old_div((toolpaths[0][seg][vertex][Y]*xyscale + yoff)*WINDOW, xysize))
                path_plot.append(yplot)
                if (vert == 1):
                    c.create_text(xplot, yplot, text=str(seg)+':'+str(vertex), tag="plot_path")
            c.create_line(path_plot, tag="plot_path", fill="red")
    else:
        #
        # 3D plot
        #
        c.delete("plot_boundary")
        c.delete("plot_path")
        #
        # remove 2D scrollbars
        #
        xscrollbar.grid_forget()
        yscrollbar.grid_forget()
        #
        # draw 3D views
        #
        c.create_line([[old_div(WINDOW, 2), 0], [old_div(WINDOW, 2), WINDOW]], tag="plot_boundary", fill="blue")
        c.create_line([[0, old_div(WINDOW, 2)], [WINDOW, old_div(WINDOW, 2)]], tag="plot_boundary", fill="blue")
        c.create_text(old_div(WINDOW, 4), old_div(WINDOW, 30), text="perspective", font=("sans-serif", 12), fill="#c00000")
        c.create_text(old_div(WINDOW, 2)+old_div(WINDOW, 4), old_div(WINDOW, 30), text="front", font=("sans-serif", 12), fill="#c00000")
        c.create_text(old_div(WINDOW, 4), old_div(WINDOW, 2)+old_div(WINDOW, 30), text="side", font=("sans-serif", 12), fill="#c00000")
        c.create_text(old_div(WINDOW, 2)+old_div(WINDOW, 4), old_div(WINDOW, 2)+old_div(WINDOW, 30), text="top", font=("sans-serif", 12), fill="#c00000")
        if (boundarys == []):
            for face in range(len(faces)):
                xy_plot = []
                xz_plot = []
                yz_plot = []
                xyz_plot = []
                for vertex in range(len(faces[face])):
                    x = vertices[faces[face][vertex]-1][X]
                    y = vertices[faces[face][vertex]-1][Y]
                    z = vertices[faces[face][vertex]-1][Z]
                    xplot = old_div(WINDOW, 2) + int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = WINDOW - int((y*xyscale + yoff)*WINDOW*0.5/xysize)
                    xy_plot.append(xplot)
                    xy_plot.append(yplot)
                    xplot = old_div(WINDOW, 2) + int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = -int((z*zscale + zoff)*WINDOW*0.5/zsize)
                    xz_plot.append(xplot)
                    xz_plot.append(yplot)
                    xplot = -int((z*zscale + zoff)*WINDOW*0.5/zsize)
                    yplot = WINDOW - int((y*xyscale + yoff)*WINDOW*0.5/xysize)
                    yz_plot.append(xplot)
                    yz_plot.append(yplot)
                    xplot = int((x*xyscale+xoff)*WINDOW*0.5/xysize)
                    yplot = old_div(WINDOW, 2) - int((y*xyscale + yoff)*WINDOW*0.5/xysize) - \
                        int((z*zscale + zoff)*WINDOW*0.5/(10*zsize))
                    xyz_plot.append(xplot)
                    xyz_plot.append(yplot)
                c.create_line(xy_plot, tag="plot_boundary")
                c.create_line(xz_plot, tag="plot_boundary")
                c.create_line(yz_plot, tag="plot_boundary")
                c.create_line(xyz_plot, tag="plot_boundary")
        for layer in range(len(boundarys)):
            for seg in range(len(boundarys[layer])):
                xy_plot = []
                xz_plot = []
                yz_plot = []
                xyz_plot = []
                for vertex in range(len(boundarys[layer][seg])):
                    x = boundarys[layer][seg][vertex][X3]
                    y = boundarys[layer][seg][vertex][Y3]
                    z = boundarys[layer][seg][vertex][Z3]
                    xplot = old_div(WINDOW, 2) + int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = WINDOW - int((y*xyscale + yoff)*WINDOW*0.5/xysize)
                    xy_plot.append(xplot)
                    xy_plot.append(yplot)
                    xplot = old_div(WINDOW, 2) + int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = -int((z*zscale + zoff)*WINDOW*0.5/zsize)
                    xz_plot.append(xplot)
                    xz_plot.append(yplot)
                    xplot = -int((z*zscale + zoff)*WINDOW*0.5/zsize)
                    yplot = WINDOW - int((y*xyscale + yoff)*WINDOW*0.5/xysize)
                    yz_plot.append(xplot)
                    yz_plot.append(yplot)
                    xplot = int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = old_div(WINDOW, 2) - int((y*xyscale + yoff)*WINDOW*0.5/xysize) - \
                        int((z*zscale + zoff)*WINDOW*0.5/(10*zsize))
                    xyz_plot.append(xplot)
                    xyz_plot.append(yplot)
                c.create_line(xy_plot, tag="plot_boundary")
                c.create_line(xz_plot, tag="plot_boundary")
                c.create_line(yz_plot, tag="plot_boundary")
                c.create_line(xyz_plot, tag="plot_boundary")
        for layer in range(len(toolpaths)):
            for seg in range(len(toolpaths[layer])):
                xy_plot = []
                xz_plot = []
                yz_plot = []
                xyz_plot = []
                for vertex in range(len(toolpaths[layer][seg])):
                    x = toolpaths[layer][seg][vertex][X3]
                    y = toolpaths[layer][seg][vertex][Y3]
                    z = toolpaths[layer][seg][vertex][Z3]
                    xplot = old_div(WINDOW, 2) + int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = WINDOW - int((y*xyscale + yoff)*WINDOW*0.5/xysize)
                    xy_plot.append(xplot)
                    xy_plot.append(yplot)
                    xplot = old_div(WINDOW, 2) + int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = -int((z*zscale + zoff)*WINDOW*0.5/zsize)
                    xz_plot.append(xplot)
                    xz_plot.append(yplot)
                    xplot = -int((z*zscale + zoff)*WINDOW*0.5/zsize)
                    yplot = WINDOW - int((y*xyscale + yoff)*WINDOW*0.5/xysize)
                    yz_plot.append(xplot)
                    yz_plot.append(yplot)
                    xplot = int((x*xyscale + xoff)*WINDOW*0.5/xysize)
                    yplot = old_div(WINDOW, 2) - int((y*xyscale + yoff)*WINDOW*0.5/xysize) - \
                        int((z*zscale + zoff)*WINDOW*0.5/(10*zsize))
                    xyz_plot.append(xplot)
                    xyz_plot.append(yplot)
                c.create_line(xy_plot, tag="plot_path", fill="red")
                c.create_line(xz_plot, tag="plot_path", fill="red")
                c.create_line(yz_plot, tag="plot_path", fill="red")
                c.create_line(xyz_plot, tag="plot_path", fill="red")


def plot_delete(event):
    global boundarys, toolpaths, contours
    #
    # scale and plot boundary, delete toolpath
    #
    for layer in range(len(toolpaths)):
        toolpaths[layer] = []
        contours[layer] = []
#   print "deleted toolpath"
    plot(event)


def delframes():
    #
    # delete all CAM frames
    #
    intext = infile.get()
    if ((find(intext, ".cmp") != -1) | (find(intext, ".CMP") != -1)
        | (find(intext, ".sol") != -1) | (find(intext, ".SOL") != -1)
        | (find(intext, ".via") != -1) | (find(intext, ".VIA") != -1)
            | (find(intext, ".mill") != -1) | (find(intext, ".MILL") != -1)):
        unionbtn.pack_forget()
    else:
        unionbtn.pack()
    camframe.pack_forget()
    cutframe.pack_forget()
    imgframe.pack_forget()
    toolframe.pack_forget()
    feedframe.pack_forget()
    zcoordframe.pack_forget()
    z2Dframe.pack_forget()
    zsliceframe.pack_forget()
    gframe.pack_forget()
    laserframe.pack_forget()
    excimerframe.pack_forget()
    autofocusframe.pack_forget()
    jetframe.pack_forget()
    out3Dframe.pack_forget()


def camselect(event):
    global faces, xmin, xmax, ymin, ymax, zmin, zmax, xysize, zsize, fixed_size
    #
    # pack appropriate CAM GUI options based on output file
    #
    xyscale = float(sxyscale.get())
    zscale = float(szscale.get())
    outtext = outfile.get()
    if (find(outtext, ".rml") != -1):
        delframes()
        camframe.pack()
        if (not fixed_size):
            sxysize.set("8")
            szsize.set("8")
        sxyvel.set("4")
        szvel.set("4")
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            szsize.set(sxysize.get())
            zcoordframe.pack()
        else:
            szup.set("0.05")
            szdown.set("-0.005")
            z2Dframe.pack()
        sdia.set("0.0156")
        sundercut.set("0.00")
        soverlap.set("0.8")
        feedframe.pack()
        toolframe.pack()
    elif (find(outtext, ".camm") != -1):
        delframes()
        camframe.pack()
        if (not fixed_size):
            sxysize.set("6")
            szsize.set("6")
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            zcoordframe.pack()
        sforce.set("45")
        svel.set("2")
        sdia.set("0.01")
        sundercut.set("0.005")
        soverlap.set("1.0")
        toolframe.pack()
        cutframe.pack()
    elif (find(outtext, ".epi") != -1):
        delframes()
        camframe.pack()
        if (not fixed_size):
            sxysize.set("24")
            szsize.set("24")
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            zcoordframe.pack()
            laserzframe.pack()
        sheight.set("10")
        srate.set("2500")
        spower.set("50")
        sspeed.set("50")
        laserframe.pack()
        sdia.set("0.01")
        sundercut.set("0.00")
        soverlap.set("0.8")
        autofocusframe.pack()
        toolframe.pack()
    elif (find(outtext, ".uni") != -1):
        delframes()
        camframe.pack()
        if (not fixed_size):
            sxysize.set("24")
            szsize.set("24")
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            zcoordframe.pack()
            laserzframe.pack()
        sheight.set("18")
        srate.set("500")
        spower.set("10")
        sspeed.set("10")
        laserframe.pack()
        sdia.set("0.01")
        sundercut.set("0.00")
        soverlap.set("0.8")
        toolframe.pack()
    elif (find(outtext, ".g") != -1):
        delframes()
        camframe.pack()
        if (not fixed_size):
            sxysize.set("24")
            szsize.set("24")
        sxyvel.set("2")
        szvel.set("2")
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            zcoordframe.pack()
        else:
            szup.set("0.05")
            szdown.set("-0.005")
            z2Dframe.pack()
        sdia.set("0.0156")
        sundercut.set("0.00")
        soverlap.set("0.8")
        toolframe.pack()
        sfeed.set("5")
        sspindle.set("5000")
        stool.set("1")
        gframe.pack()
    elif ((find(outtext, ".jpg") != -1) | (find(outtext, ".bmp") != -1)):
        delframes()
        camframe.pack()
        sdia.set("0.015")
        sundercut.set("0.00")
        soverlap.set("0.8")
        toolframe.pack()
        sximg.set("500")
        syimg.set("500")
        imgframe.pack()
        xysize = float(sxysize.get())
        if ((xmax-xmin) > (ymax-ymin)):
            xyscale = old_div(xysize, (xmax - xmin))
            sxyscale.set(str(xyscale))
            xoff = old_div(-(xmin*xysize), (xmax-xmin))
            yoff = old_div(-(ymin*xysize), (xmax-xmin))
            sxmin.set(str(xoff))
            symin.set(str(yoff))
        else:
            xyscale = old_div(xysize, (ymax - ymin))
            sxyscale.set(str(xyscale))
            yoff = old_div(-(ymin*xysize), (ymax-ymin))
            xoff = old_div(-(xmin*xysize), (ymax-ymin))
            sxmin.set(str(xoff))
            symin.set(str(yoff))
    elif (find(outtext, ".ord") != -1):
        delframes()
        camframe.pack()
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            zcoordframe.pack()
        if (not fixed_size):
            sxysize.set("24")
        sdia.set("0.01")
        sundercut.set("0.005")
        soverlap.set("1.0")
        toolframe.pack()
        slead.set("0.1")
        squality.set("-3")
        jetframe.pack()
    elif (find(outtext, ".oms") != -1):
        delframes()
        camframe.pack()
        if (faces != []):
            sztop.set(str(zmax))
            szbot.set(str(zmin))
            sthickness.set(str(zmax-zmin))
            zsliceframe.pack()
        if ((faces != []) | (len(boundarys) > 1)):
            zcoordframe.pack()
        if (not fixed_size):
            sxysize.set("1")
        spulseperiod.set("10000")
        scutvel.set("0.1")
        scutaccel.set("5.0")
        excimerframe.pack()
        sdia.set(".001")
        sundercut.set("0.00")
        soverlap.set("0.8")
        toolframe.pack()
    elif (find(outtext, ".dxf") != -1):
        delframes()
        sdia.set("0.0156")
        sundercut.set("0.00")
        soverlap.set("0.8")
        camframe.pack()
        toolframe.pack()
    elif (find(outtext, ".stl") != -1):
        delframes()
        sthickness.set("0.1")
        out3Dframe.pack()
        zcoordframe.pack()
    else:
        print("output file format not supported")
#   plot(event)
    plot_delete(event)
    return


def devselect(event):
    #
    # select the output device
    #
    sel = wdevlist.get(wdevlist.curselection())
    cur_sel = outfile.get()
    dot = find(cur_sel, '.')
    cur_sel = cur_sel[(dot+1):]
    if ((sel[0:3] == 'epi') & (cur_sel != 'epi')):
        outfile.set('out.epi')
        camselect(0)
    elif ((sel[0:3] == 'oms') & (cur_sel != 'oms')):
        outfile.set('out.oms')
        camselect(0)
    elif ((sel[0:3] == 'ord') & (cur_sel != 'ord')):
        outfile.set('out.ord')
        camselect(0)
    elif ((sel[0:2] == 'g:') & (cur_sel != 'g')):
        outfile.set('out.g')
        camselect(0)
    elif ((sel[0:3] == 'bmp') & (cur_sel != 'bmp')):
        outfile.set('out.bmp')
        camselect(0)
    elif ((sel[0:3] == 'jpg') & (cur_sel != 'jpg')):
        outfile.set('out.jpg')
        camselect(0)
    elif ((sel[0:3] == 'stl') & (cur_sel != 'stl')):
        outfile.set('out.stl')
        camselect(0)
    elif ((sel[0:3] == 'dxf') & (cur_sel != 'dxf')):
        outfile.set('out.dxf')
        camselect(0)
    elif ((sel[0:3] == 'uni') & (cur_sel != 'uni')):
        outfile.set('out.uni')
        camselect(0)
    elif ((sel[0:3] == 'rml') & (cur_sel != 'rml')):
        outfile.set('out.rml')
        camselect(0)
    elif ((sel[0:4] == 'camm') & (cur_sel != 'camm')):
        outfile.set('out.camm')
        camselect(0)


def send(event):
    #
    # send to the output device
    #
    outtext = outfile.get()
    if (find(outtext, ".rml") != -1):
        wdevbtn.config(text="sending ...")
        wdevbtn.update()
        write(event)
        print(os.system('stty 9600 raw -echo crtscts </dev/ttyS0'))
        print(os.system('cat %s > /dev/ttyS0' % outtext))
        print(os.system('rm %s' % outtext))
        wdevbtn.config(text="send to")
        # wdevbtn.update()
    elif (find(outtext, ".camm") != -1):
        wdevbtn.config(text="sending ...")
        wdevbtn.update()
        write(event)
        print(os.system('stty 9600 raw -echo crtscts </dev/ttyS0'))
        print(os.system('cat %s > /dev/ttyS0' % outtext))
        print(os.system('rm %s' % outtext))
        wdevbtn.config(text="send to")
        # wdevbtn.update()
    elif (find(outtext, ".epi") != -1):
        wdevbtn.config(text="sending ...")
        wdevbtn.update()
        write(event)
        print(os.system('lpr -P Queue %s' % outtext))
        print(os.system('rm %s' % outtext))
        wdevbtn.config(text="send to")
        # wdevbtn.update()
    else:
        print("output not configured for", outtext)


def openfile():
    #
    # dialog to select an input file
    #
    filename = askopenfilename()
    infile.set(filename)
    read(0)


def savefile():
    #
    # dialog to select an output file
    #
    filename = asksaveasfilename()
    outfile.set(filename)
    camselect(0)


root = Tk()
root.title('cam.py')
root.bind('Q', 'exit')

print("cam.py "+DATE+" (c) MIT CBA Neil Gershenfeld")
print("""Permission granted for experimental and personal use;
   license for commercial sale available from MIT""")
print(prompt)

#
# parse input command line arguments
#
infile = StringVar()
infile.set('')
outfile = StringVar()
outfile.set('out.epi')
xmin = 0.0
xmax = 0.0
ymin = 0.0
ymax = 0.0
zmin = -1.0
zmax = 0.0
xyscale = 1.0
zscale = 1.0
xysize = 1.0
zsize = 1.0
nverts = 10
fixed_size = False
jobname = ""
for i in range(len(sys.argv)):
    if (find(sys.argv[i], "-o") != -1):
        outfile.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-d") != -1):
        xysize = float(sys.argv[i+1])
        fixed_size = True
    elif (find(sys.argv[i], "-p") != -1):
        xyscale = float(sys.argv[i+1])
    elif (find(sys.argv[i], "-x") != -1):
        xmin = float(sys.argv[i+1])
    elif (find(sys.argv[i], "-y") != -1):
        ymin = float(sys.argv[i+1])
    elif (find(sys.argv[i], "-i") != -1):
        infile.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-n") != -1):
        noise_flag = 0
    elif (find(sys.argv[i], "-#") != -1):
        nverts = int(sys.argv[i+1])
    elif (find(sys.argv[i], "-j") != -1):
        jobname = sys.argv[i+1]
if (len(sys.argv) > 1):
    if (sys.argv[1][0] != '-'):
        infile.set(sys.argv[1])
sxmin = StringVar()
sxmin.set(str(xmin))
symin = StringVar()
symin.set(str(ymin))
szmax = StringVar()
szmax.set(str(zmax))
sxyscale = StringVar()
sxyscale.set(str(xyscale))
szscale = StringVar()
szscale.set(str(zscale))
sxysize = StringVar()
sxysize.set(str(xysize))
szsize = StringVar()
szsize.set(str(zsize))
#
# define GUI
#
inframe = Frame(root)
inbtn = Button(inframe, text="input file:", command=openfile)
inbtn.pack(side="left")
winfile = Entry(inframe, width=15, textvariable=infile)
winfile.pack(side="left")
winfile.bind('<Return>', read)
Label(inframe, text=" ").pack(side="left")
Label(inframe, text="xy display size:").pack(side="left")
wxysize = Entry(inframe, width=4, textvariable=sxysize)
wxysize.pack(side="left")
wxysize.bind('<Return>', plot)
Label(inframe, text=" scale:").pack(side="left")
autobtn = Button(inframe, text="auto")
autobtn.bind('<Button-1>', autoscale)
autobtn.pack(side="left")
fixedbtn = Button(inframe, text="fixed")
fixedbtn.bind('<Button-1>', fixedscale)
fixedbtn.pack(side="left")
Label(inframe, text=" ").pack(side="left")
ivert = IntVar()
wvert = Checkbutton(inframe, text="show vertices", variable=ivert)
# wvert.pack(side="left")
# wvert.bind('<ButtonRelease-1>',plot)
inframe.pack()
#
xycoordframe = Frame(root)
Label(xycoordframe, text=" x min:").pack(side="left")
wxmin = Entry(xycoordframe, width=6, textvariable=sxmin)
wxmin.pack(side="left")
wxmin.bind('<Return>', plot)
Label(xycoordframe, text=" y min:").pack(side="left")
wymin = Entry(xycoordframe, width=6, textvariable=symin)
wymin.pack(side="left")
wymin.bind('<Return>', plot)
Label(xycoordframe, text=" xy scale factor:").pack(side="left")
wxyscale = Entry(xycoordframe, width=6, textvariable=sxyscale)
wxyscale.pack(side="left")
wxyscale.bind('<Return>', plot_delete)
sdxy = StringVar()
Label(xycoordframe, textvariable=sdxy).pack(side="left")
xycoordframe.pack()
#
zcoordframe = Frame(root)
Label(zcoordframe, text="z max: ").pack(side="left")
wzmax = Entry(zcoordframe, width=6, textvariable=szmax)
wzmax.bind('<Return>', plot)
wzmax.pack(side="left")
Label(zcoordframe, text="z scale factor:").pack(side="left")
wzscale = Entry(zcoordframe, width=6, textvariable=szscale)
wzscale.bind('<Return>', plot)
wzscale.pack(side="left")
Label(zcoordframe, text="z display size:").pack(side="left")
wzsize = Entry(zcoordframe, width=6, textvariable=szsize)
wzsize.bind('<Return>', plot)
wzsize.pack(side="left")
sdz = StringVar()
Label(zcoordframe, textvariable=sdz).pack(side="left")
zcoordframe.pack()
#
canvasframe = Frame(root)
xscrollbar = Scrollbar(canvasframe, orient=HORIZONTAL)
xscrollbar.grid(row=1, column=0, sticky=E+W)
yscrollbar = Scrollbar(canvasframe)
yscrollbar.grid(row=0, column=1, sticky=N+S)
c = Canvas(canvasframe, width=WINDOW, height=WINDOW, background='white',
           xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
c.grid(row=0, column=0, sticky=N+S+E+W)
c.configure(scrollregion=(0, 0, WINDOW, WINDOW))
xscrollbar.config(command=c.xview)
yscrollbar.config(command=c.yview)
canvasframe.pack()
#
outframe = Frame(root)
#
Logo = Canvas(outframe, width=26, height=26, background="white")
Logo.create_oval(2, 2, 8, 8, fill="red", outline="")
Logo.create_rectangle(11, 2, 17, 8, fill="blue", outline="")
Logo.create_rectangle(20, 2, 26, 8, fill="blue", outline="")
Logo.create_rectangle(2, 11, 8, 17, fill="blue", outline="")
Logo.create_oval(10, 10, 16, 16, fill="red", outline="")
Logo.create_rectangle(20, 11, 26, 17, fill="blue", outline="")
Logo.create_rectangle(2, 20, 8, 26, fill="blue", outline="")
Logo.create_rectangle(11, 20, 17, 26, fill="blue", outline="")
Logo.create_rectangle(20, 20, 26, 26, fill="blue", outline="")
Logo.pack(side="left")
status = StringVar()
namedate = "   cam.py ("+DATE+")  "
status.set(namedate)
Label(outframe, textvariable=status).pack(side="left")
outbtn = Button(outframe, text="output file:", command=savefile)
outbtn.pack(side="left")
woutfile = Entry(outframe, width=15, textvariable=outfile)
woutfile.bind('<Return>', camselect)
woutfile.pack(side="left")
Label(outframe, text=" ").pack(side="left")
Button(outframe, text="quit", command='exit').pack(side="left")
Label(outframe, text=" ").pack(side="left")
outframe.pack()
#
devframe = Frame(root)
wdevbtn = Button(devframe, text="send to")
wdevbtn.bind('<Button-1>', send)
wdevbtn.pack(side="left")
Label(devframe, text=" output device: ").pack(side="left")
wdevscroll = Scrollbar(devframe, orient=VERTICAL)
wdevlist = Listbox(devframe, width=40, height=1, yscrollcommand=wdevscroll.set)
wdevlist.bind('<ButtonRelease-1>', devselect)
wdevscroll.config(command=wdevlist.yview)
wdevscroll.pack(side=RIGHT, fill='y')
wdevlist.insert(END, "epi: Epilog lasercutter")
wdevlist.insert(END, "oms: Resonetics excimer micromachining center")
wdevlist.insert(END, "ord: OMAX waterjet cutter")
wdevlist.insert(END, "g: G code file")
wdevlist.insert(END, "bmp: image")
wdevlist.insert(END, "jpg: image")
wdevlist.insert(END, "stl: object")
wdevlist.insert(END, "dxf: drawing")
wdevlist.insert(END, "uni: Universal lasercutter")
wdevlist.insert(END, "rml: Roland Modela NC mill")
wdevlist.insert(END, "camm: Roland CAMM vinyl cutter")
wdevlist.pack(side=LEFT, fill=BOTH)
wdevlist.select_set(0)
devframe.pack()
#
camframe = Frame(root)
contourbtn = Button(camframe, text="contour boundary")
contourbtn.bind('<Button-1>', contour)
contourbtn.pack(side="left")
Label(camframe, text=" ").pack(side="left")
rasterbtn = Button(camframe, text="raster interior")
rasterbtn.bind('<Button-1>', raster)
rasterbtn.pack(side="left")
Label(camframe, text=" ").pack(side="left")
writebtn = Button(camframe, text="write toolpath")
writebtn.bind('<Button-1>', write)
writebtn.pack(side="left")
Label(camframe, text=" ").pack(side="left")
unionbtn = Button(camframe, text="union polygons")
unionbtn.bind('<Button-1>', union_boundary)
unionbtn.pack(side="left")
camframe.pack()
#
toolframe = Frame(root)
Label(toolframe, text="tool diameter: ").pack(side="left")
sdia = StringVar()
wtooldia = Entry(toolframe, width=6, textvariable=sdia)
wtooldia.pack(side="left")
wtooldia.bind('<Return>', plot_delete)
#Label(toolframe, text=" N contour: ").pack(side="left")
#sncontour = StringVar()
#wncontour = Entry(toolframe, width=3, textvariable=sncontour)
# wncontour.pack(side="left")
# wncontour.bind('<Return>',plot_delete)
Label(toolframe, text=" contour undercut: ").pack(side="left")
sundercut = StringVar()
wundercut = Entry(toolframe, width=6, textvariable=sundercut)
wundercut.pack(side="left")
wundercut.bind('<Return>', plot_delete)
Label(toolframe, text=" raster overlap: ").pack(side="left")
soverlap = StringVar()
woverlap = Entry(toolframe, width=6, textvariable=soverlap)
woverlap.pack(side="left")
woverlap.bind('<Return>', plot_delete)
#
feedframe = Frame(root)
Label(feedframe, text=" xy speed:").pack(side="left")
sxyvel = StringVar()
Entry(feedframe, width=10, textvariable=sxyvel).pack(side="left")
Label(feedframe, text=" z speed:").pack(side="left")
szvel = StringVar()
Entry(feedframe, width=10, textvariable=szvel).pack(side="left")
#
z2Dframe = Frame(root)
Label(z2Dframe, text="z up:").pack(side="left")
szup = StringVar()
Entry(z2Dframe, width=10, textvariable=szup).pack(side="left")
Label(z2Dframe, text=" z down:").pack(side="left")
szdown = StringVar()
Entry(z2Dframe, width=10, textvariable=szdown).pack(side="left")
#
zsliceframe = Frame(root)
zslicebtn = Button(zsliceframe, text="z slice")
zslicebtn.bind('<Button-1>', zslice)
zslicebtn.pack(side="left")
Label(zsliceframe, text=" ").pack(side="left")
Label(zsliceframe, text=" top: ").pack(side="left")
sztop = StringVar()
sztop.set("0")
wztop = Entry(zsliceframe, width=10, textvariable=sztop)
wztop.pack(side="left")
Label(zsliceframe, text=" bottom: ").pack(side="left")
szbot = StringVar()
szbot.set("-1")
wzbot = Entry(zsliceframe, width=10, textvariable=szbot)
wzbot.pack(side="left")
Label(zsliceframe, text=" thickness: ").pack(side="left")
sthickness = StringVar()
sthickness.set("1")
wthickness = Entry(zsliceframe, width=10, textvariable=sthickness)
wthickness.pack(side="left")
#
gframe = Frame(root)
Label(gframe, text=" feed rate:").pack(side="left")
sfeed = StringVar()
Entry(gframe, width=6, textvariable=sfeed).pack(side="left")
Label(gframe, text=" spindle speed:").pack(side="left")
sspindle = StringVar()
Entry(gframe, width=6, textvariable=sspindle).pack(side="left")
Label(gframe, text=" tool:").pack(side="left")
stool = StringVar()
Entry(gframe, width=3, textvariable=stool).pack(side="left")
icool = IntVar()
wcool = Checkbutton(gframe, text="coolant", variable=icool)
wcool.pack(side="left")
#
cutframe = Frame(root)
Label(cutframe, text="force: ").pack(side="left")
sforce = StringVar()
Entry(cutframe, width=10, textvariable=sforce).pack(side="left")
Label(cutframe, text=" velocity:").pack(side="left")
svel = StringVar()
Entry(cutframe, width=10, textvariable=svel).pack(side="left")
#
laserframe = Frame(root)
Label(laserframe, text="bed height: ").pack(side="left")
sheight = StringVar()
Entry(laserframe, width=10, textvariable=sheight).pack(side="left")
Label(laserframe, text=" rate: ").pack(side="left")
srate = StringVar()
Entry(laserframe, width=10, textvariable=srate).pack(side="left")
Label(laserframe, text=" power:").pack(side="left")
spower = StringVar()
Entry(laserframe, width=10, textvariable=spower).pack(side="left")
Label(laserframe, text=" speed:").pack(side="left")
sspeed = StringVar()
Entry(laserframe, width=10, textvariable=sspeed).pack(side="left")
#
laserzframe = Frame(root)
Label(laserzframe, text="z max power: ").pack(side="left")
szmaxpower = StringVar()
szmaxpower.set("100")
Entry(laserzframe, width=3, textvariable=szmaxpower).pack(side="left")
Label(laserzframe, text="%     z min power: ").pack(side="left")
szminpower = StringVar()
szminpower.set("0")
Entry(laserzframe, width=3, textvariable=szminpower).pack(side="left")
Label(laserzframe, text="%").pack(side="left")
#
autofocusframe = Frame(root)
iautofocus = IntVar()
wautofocus = Checkbutton(autofocusframe, text="Auto Focus", variable=iautofocus).pack(side="left")
#
imgframe = Frame(root)
Label(imgframe, text="x size (pixels): ").pack(side="left")
sximg = StringVar()
Entry(imgframe, width=10, textvariable=sximg).pack(side="left")
Label(imgframe, text=" y size (pixels):").pack(side="left")
syimg = StringVar()
Entry(imgframe, width=10, textvariable=syimg).pack(side="left")
#
jetframe = Frame(root)
Label(jetframe, text="lead-in/out: ").pack(side="left")
slead = StringVar()
wlead = Entry(jetframe, width=4, textvariable=slead)
wlead.pack(side="left")
Label(jetframe, text="quality: ").pack(side="left")
squality = StringVar()
wquality = Entry(jetframe, width=4, textvariable=squality)
wquality.pack(side="left")
#
excimerframe = Frame(root)
Label(excimerframe, text="pulse period (usec): ").pack(side="left")
spulseperiod = StringVar()
wpulseperiod = Entry(excimerframe, width=5, textvariable=spulseperiod)
wpulseperiod.pack(side="left")
Label(excimerframe, text="cut velocity: ").pack(side="left")
scutvel = StringVar()
wcutvel = Entry(excimerframe, width=4, textvariable=scutvel)
wcutvel.pack(side="left")
Label(excimerframe, text="cut acceleration: ").pack(side="left")
scutaccel = StringVar()
wcutaccel = Entry(excimerframe, width=4, textvariable=scutaccel)
wcutaccel.pack(side="left")
#
out3Dframe = Frame(root)
extrudebtn = Button(out3Dframe, text="extrude")
extrudebtn.bind('<Button-1>', extrude)
extrudebtn.pack(side="left")
Label(out3Dframe, text="thickness: ").pack(side="left")
sextrude = StringVar()
wextrude = Entry(out3Dframe, width=6, textvariable=sextrude)
wextrude.pack(side="left")
Label(out3Dframe, text=" ").pack(side="left")
write3Dbtn = Button(out3Dframe, text="write file")
write3Dbtn.bind('<Button-1>', write)
write3Dbtn.pack(side="left")
#
# read input file and set up GUI
#
if (infile.get() != ''):
    read(0)
else:
    camselect(0)
#
# parse output command line arguments
#
for i in range(len(sys.argv)):
    if (find(sys.argv[i], "-f") != -1):
        sforce.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-v") != -1):
        svel.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-t") != -1):
        sdia.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-a") != -1):
        srate.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-e") != -1):
        spower.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-s") != -1):
        sspeed.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-h") != -1):
        sheight.set(sys.argv[i+1])
    elif (find(sys.argv[i], "-c") != -1):
        contour(0)
    elif (find(sys.argv[i], "-r") != -1):
        raster(0)
    elif (find(sys.argv[i], "-w") != -1):
        write(0)
        sys.exit()
#
# start GUI
#
root.mainloop()
