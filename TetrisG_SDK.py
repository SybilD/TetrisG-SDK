# -*- coding: utf-8 -*-
"""TetrisG_SDK.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VChdogGRU4HdeGnRhwjuyb31Rb0_t7bG
"""

def network_information(network, image) :
    print("="*50)
    print(" Network : ", network)
    print( " Array Size = {} x {}".format(array[0], array[1]))
    print("-"*30)

    print(" NETWORK INFORMATION ")
    print("-"*30)
    for i in range(len(image)) :
        print(" CONV LAYER "+ str(i+1))
        print("    Image   Size = {} x {}".format(image[i], image[i]))
        print("    Kernel  Size = {} x {}".format(kernel[i], kernel[i]))
        if network == 'VGG13' :
          print("    Channel Size = {} x {}".format(channel[i], channel[i+1]))
        elif network == 'Resnet13' :
          print("    Channel Size = {} x {}".format(channel[i], channel[i]))
    print("="*50)

import math
import seaborn as sns
import matplotlib.pyplot as plt
import random
import numpy as np


def im2col (image_col, image_row, filter_col, filter_row, in_channel, out_channel, array_row, array_col) :

    col_slide = image_col - filter_col + 1
    row_slide = image_row - filter_row + 1

    col_cycle = math.ceil(out_channel/array_col)

    # 우선 첫 cycle의 매핑을 보여주기위해 세팅
    if col_cycle > 1 :
        o_ct = array_col
    else :
        o_ct = out_channel

    i_ct = math.floor(array_row/(filter_col*filter_row))
    row_cycle = math.ceil(in_channel/i_ct)
    total_cycle = col_slide * row_slide * row_cycle * col_cycle

    return total_cycle, i_ct, o_ct

def SDK (image_col, image_row, filter_col, filter_row, in_channel, out_channel, \
                    array_row, array_col) :

    row_vector = filter_row * filter_col * in_channel
    col_vector = out_channel

    used_row = math.ceil(row_vector/array_row)
    used_col = math.ceil(col_vector/array_col)

    new_array_row = array_row * used_row
    new_array_col = array_col * used_col

    # initialize
    cycle = []
    w = [] # pw 크기
    w.append(filter_row*filter_col)
    cycle.append(used_row*used_col*(image_row-filter_row+1)*(image_col-filter_col+1))

    i=0
    while True :
        i += 1
        pw_row = filter_row + i - 1
        pw_col = filter_col + i - 1
        pw = pw_row * pw_col
        if pw*in_channel <= new_array_row and i * i * out_channel <= new_array_col :
            parallel_window_row = math.ceil((image_row - (filter_row + i) + 1)/i) + 1
            parallel_window_col = math.ceil((image_col - (filter_col + i) + 1)/i) + 1

            if parallel_window_row * parallel_window_row * used_row * used_col <= cycle[0] :
                del cycle[0]
                del w[0]
                cycle.append(parallel_window_row * parallel_window_col * used_row * used_col)
                w.append(pw)

        else :
            break

    return cycle, w

# ceil : up, floor : down
def vw_sdk (image_col, image_row, filter_col, filter_row, in_channel, out_channel, \
                    array_row, array_col) :

    i = 0 # initialize # overlap col
    j = 1 # overlap row

    reg_total_cycle = [] # initialize
    reg_overlap_row = []
    reg_overlap_col = []
    reg_row_cycle = []
    reg_col_cycle = []
    reg_ICt = []
    reg_OCt = []

    while True :
        try :
            i += 1
            if (i + filter_col) > image_col :
                i = 1
                j += 1
                if j + filter_row > image_row :
                    break

            # for parallel_window computing
            reg_N_parallel_window_row = math.ceil((image_row - (filter_row + i) + 1)/i) + 1
            reg_N_parallel_window_col = math.ceil((image_col - (filter_col + j) + 1)/j) + 1

            # for cycle computing
            # Tiled IC
            if in_channel == 3 :
                ICt = math.floor(array_row /((filter_row + i - 1)*(filter_col + j - 1)))
                if ICt > in_channel :
                    ICt = 3
                row_cycle = math.ceil(in_channel / ICt)
            else :
                ICt = math.floor(array_row /((filter_row + i - 1)*(filter_col + j - 1)))
                row_cycle = math.ceil(in_channel / ICt)

            # Tiled OC
            OCt =  math.floor(array_col / (i * j))
            col_cycle = math.ceil(out_channel / OCt)

            reg_N_of_computing_cycle = reg_N_parallel_window_row * reg_N_parallel_window_col \
                                    * row_cycle * col_cycle

            if i == 1 : # initialize
                reg_total_cycle.append(reg_N_of_computing_cycle)
                reg_overlap_row.append(i)
                reg_overlap_col.append(j)
                reg_row_cycle.append(row_cycle)
                reg_col_cycle.append(col_cycle)
                reg_ICt.append(ICt)
                reg_OCt.append(OCt)

            if reg_total_cycle[0] > reg_N_of_computing_cycle :
                del reg_total_cycle[0]
                del reg_overlap_row[0]
                del reg_overlap_col[0]
                del reg_row_cycle[0]
                del reg_col_cycle[0]
                del reg_ICt[0]
                del reg_OCt[0]

                reg_total_cycle.append(reg_N_of_computing_cycle)
                reg_overlap_row.append(i)
                reg_overlap_col.append(j)
                reg_row_cycle.append(row_cycle)
                reg_col_cycle.append(col_cycle)
                reg_ICt.append(ICt)
                reg_OCt.append(OCt)


        except ZeroDivisionError :
            continue

    return reg_total_cycle[0], reg_overlap_col[0], reg_overlap_row[0], reg_row_cycle[0], reg_col_cycle[0], reg_ICt[0], reg_OCt[0]

def result_vw (image, kernel, IC, OC, array_row, array_col, method) :

    VWSDK_height = []
    VWSDK_width = []
    AR_cycle = []
    AC_cycle = []
    VW_IC_tiled = []
    VW_OC_tiled = []

    CC=[]
    print("="*50)
    print(" RESULTS of COMPUTING CYCLES")
    print("-"*30)

    T_cycle_vw, VWSDK_h, VWSDK_w, ARC, ACC, tiled_IC, tiled_OC = vw_sdk(image, image, kernel, kernel, IC, OC, array_row, array_col)
    CC.append(T_cycle_vw)
    VWSDK_height.append(VWSDK_h)
    VWSDK_width.append(VWSDK_w)
    AR_cycle.append(ARC)
    AC_cycle.append(ACC)
    VW_IC_tiled.append(tiled_IC)
    VW_OC_tiled.append(tiled_OC)

    T_cycle_im, i_ct, o_ct = im2col(image, image, kernel, kernel, IC, OC, array_row, array_col)
    T_cycle_SDK, pw = SDK(image, image, kernel, kernel, IC, OC, array_row, array_col)

    SDK_w, SDK_h = math.sqrt(pw[0])-kernel+1, math.sqrt(pw[0])-kernel+1
    SDK_ict = math.floor(array_row /((kernel + SDK_w - 1)*(kernel + SDK_h - 1)))
    SDK_oct = math.floor(array_col / (SDK_w * SDK_h))

    print("    Im2col = {}".format(T_cycle_im))
    print("     S D K = {}".format(T_cycle_SDK[0]))
    print("     S D K = {}".format(pw[0]))
    print("    VW-SDK = {}".format(CC[0]))
    print("      - Optimal shape of PW = {} x {} x {} x {}".format(kernel + VWSDK_width[0]-1, kernel + VWSDK_height[0]-1, VW_IC_tiled[0], VW_OC_tiled[0]))
    print("="*50)
    pw_row, pw_col, pw_ic, pw_oc = kernel + VWSDK_width[0]-1, kernel + VWSDK_height[0]-1, VW_IC_tiled[0], VW_OC_tiled[0]

    return pw_row, pw_col, pw_ic, pw_oc

# definations

# ckecking marginal space
def marginal_optimizable_row(image, kernel, pw_row):
  if (image-pw_row)%(pw_row - kernel +1) != 0:
    return True
  else:
    return False

def marginal_optimizable_col(image, kernel, pw_col):
  if (image-pw_col)%(pw_col - kernel +1) != 0:
    return True
  else:
    return False

def N_parallel_window(image,kernel,pw_row,pw_col):
  return (math.ceil((image-pw_row) /(pw_row - kernel +1)) + 1)* (math.ceil((image-pw_col) /(pw_col - kernel +1)) + 1)

def N_parallel_window_so(image,kernel,pw_row,pw_col):
  return (math.floor((image-pw_row) /(pw_row - kernel +1)) + 1)* (math.floor((image-pw_col) /(pw_col - kernel +1)) + 1)

# cc considering marginal space, and depth

# cc considering marginal space
def tetris_cc(image, kernel, ic, oc, ar, ac, pw_row, pw_col, pw_ic, pw_oc):
  No_conv = (pw_row - kernel + 1) * (pw_col - kernel + 1)
  # print("No. of conv in one original VWSDK PW is", No_conv)

  No_parallel_window = N_parallel_window(image,kernel,pw_row,pw_col)
  print("    No. of PW for the VWSDK is", No_parallel_window * math.ceil(ic / pw_ic))
  print("-"*30)
  print("    Performing Tetris-SDK")
  print("-"*30)

  optimal_N_parallel_window = No_parallel_window
  so_row = 0 #square-optimized
  so_col = 0
  No_cells = pw_row * pw_col #CIM array row occupied
  No_cells_so = No_cells
  ICt = pw_ic

  moX_row = 0 #marginal_space_window_x_direction
  moX_col = 0

  moY_row = 0
  moY_col = 0

  marginal_space_row = 0
  marginal_space_col = 0

  No_of_moX = 0
  No_of_moY = 0
  found_so = False
  ICmX = 0
  ICmY = 0

  No_windows = 0
  No_windows_so = 0
  No_remaining_parallel_window = No_parallel_window

  do_row = 0 #depth-wise optimized
  do_col = 0
  No_cells_do = No_cells
  mICt = 0

  mmoX_row = 0 #depth-wise marginal
  mmoX_col = 0

  mmoY_row = 0
  mmoY_col = 0

  mmarginal_space_row = 0
  mmarginal_space_col = 0

  No_of_mmoX = 0
  No_of_mmoY = 0

  mICmX = 0
  mICmY = 0


  for i in range(1, int(pow(No_conv, 1 / 2))+1):
        if No_conv % i == 0 and found_so == False:
          # print("FACTOR: " + str(i) +"*"+str(int(No_conv / i)))
          sw_row = i + kernel -1
          sw_col = int(No_conv / i) + kernel -1
          # print("sw_pw is", sw_row, "*", sw_col)
          # print("cc is", N_parallel_window(image,kernel,sw_row,sw_col))
          # print(N_parallel_window(image,kernel,sw_row,sw_col))
          # print(ptimal_N_parallel_window)
          if (N_parallel_window(image,kernel,sw_row,sw_col)<= optimal_N_parallel_window) and (sw_row*sw_col < No_cells) :
            optimal_N_parallel_window = N_parallel_window(image,kernel,sw_row,sw_col)
            so_row = sw_row
            so_col = sw_col
            No_cells_so = sw_row*sw_col
            ICt = ar // No_cells_so
            found_so = True
            # print("!!!!!found_so", found_so)
            # print(so_row, "x", so_col, "square-inclined window is better than the original PW", pw_row, pw_col)
            print("Square-inclined window: ", so_row, "x", so_col, "x", ICt)
            print("Number of square-inclined window:", N_parallel_window_so(image,kernel,so_row,so_col))
            if marginal_optimizable_row(image, kernel, so_row):
              marginal_space_row = (image-so_row) % (so_row - kernel +1)
              # print("marginal_space_row is",marginal_space_row) # 4
              moX_row = marginal_space_row + kernel - 1
              moX_col = (pw_row * pw_col) // moX_row
              ICmX = ar // (moX_row * moX_col)
              No_of_moX = math.ceil(((image-moX_col)/(moX_col - kernel +1)))+1
              # print("Marginal_window_row:", moX_row, "x", moX_col, ", and No_of_marginal_window_X is", No_of_moX)
              print("Marginal_window_row:", moX_row, "x", moX_col, "x", ICmX)
              print("No_of_marginal_window_row:", No_of_moX)
            else:
              # print("There is no marginal rows to be optimzed.")
              No_of_moX=0

            if marginal_optimizable_col(image, kernel, so_col):
              marginal_space_col = (image-so_col) % (so_col - kernel +1)
              # print("marginal_space_col is",marginal_space_col) # 4
              moY_col = marginal_space_col + kernel - 1
              moY_row = (pw_row * pw_col) // moY_col
              ICmY = ar // (moY_row * moY_col)
              No_of_moY = math.ceil(((image-moY_row)/(moY_row - kernel +1)))+1
              # print("marginal_window_size on cols has size", moY_row, "x", moY_col, ", and No_of_marginal_window_Y is", No_of_moY)
              print("Marginal_window_column:", moY_row, "x", moY_col, "x", ICmY)
              print("No_of_marginal_window_column:", No_of_moY)
            else:
              # print("There is no marginal cols to be optimzed.")
              No_of_moY=0

            No_windows_so = N_parallel_window_so(image,kernel,so_row,so_col)
            No_windows = ( No_windows_so + No_of_moX + No_of_moY )
            # print("!!!!!N_parallel_window_so is!!!!", No_windows_so)
            print("Number of square-inclined window and marginal window (one-tile):", No_windows)

          else:
            # print("This pair is not optimized")
            No_windows = N_parallel_window(image,kernel,sw_row,sw_col)

  if found_so == False:
            # print("found_so", found_so)
            if marginal_optimizable_row(image, kernel, pw_row):
              marginal_space_row = (image-pw_row) % (pw_row - kernel +1)
              # print("marginal_space_row is",marginal_space_row) # 4
              moX_row = marginal_space_row + kernel - 1
              moX_col = (ar/pw_ic) // moX_row
              ICmX = ar // (moX_row * moX_col)
              No_of_moX = math.ceil(((image-moX_col)/(moX_col - kernel +1)))+1
              # print("marginal_window_size on rows has size", moX_row, "x", moX_col, ", and No_of_marginal_window_X is", No_of_moX)
              print("Marginal_window_row:", moX_row, "x", moX_col, "x", ICmX)
              print("No_of_marginal_window_row:", No_of_moX)
            else:
              # print("There is no marginal rows to be optimzed.")
              No_of_moX=0

            if marginal_optimizable_col(image, kernel, pw_col):
              marginal_space_col = (image-pw_col) % (pw_col - kernel +1)
              print("marginal_space_col is",marginal_space_col) # 4
              moY_col = marginal_space_col + kernel - 1
              moY_row = (ar/pw_ic) // moY_col
              ICmY = ar // (moY_row * moY_col)
              No_of_moY = math.ceil(((image-moY_row)/(moY_row - kernel +1)))+1
              # print("marginal_window_size on cols has size", moY_row, "x", moY_col, ", and No_of_marginal_window_Y is", No_of_moY)
              print("Marginal_window_column:", moY_row, "x", moY_col, "x", ICmY)
              print("No_of_marginal_window_column:", No_of_moY)
            else:
              # print("There is no marginal cols to be optimzed.")
              No_of_moY=0

            No_windows_so = N_parallel_window_so(image,kernel,pw_row,pw_col)
            No_windows = ( No_windows_so + No_of_moX + No_of_moY )
            print("No square-inclined window can be found. Number of windows:", No_windows_so, "for", pw_row,"x", pw_col )
            print("Number of windows with marginal-optimized:", No_windows)


# calculate variable depeth
  # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
  remaining_channels = ic % ICt
  reg_remaining_channels = remaining_channels
  # print("Remaining channels: ", remaining_channels)
  No_windows = No_windows * (ic // ICt)
  print("Total number of windows with square-optimized, marginal-optimized is", No_windows)
  max_conv = ac // oc #16
  # print("Maximum convolution: ", max_conv)
  found_max = False
  found_conv = False
  # found_so = False
          # No_remaining_parallel_window

  prune = 0

  while found_max==False and (remaining_channels >0):
    # try:
      print("PRUNING", prune, "CHANNELS")
      remaining_channels -= prune
      print("Remaining channels", remaining_channels)
      for i in range(int(pow(max_conv, 1 / 2))+1,1, -1):
        if (max_conv % i == 0) and (int(max_conv / i) <= image):
                  # print("FACTOR: " + str(i) +"*"+str(int(max_conv / i)))
                  dw_row = i + kernel -1
                  dw_col = int(max_conv / i) + kernel -1
                  # print("Depth_optimal_window is", dw_row, "*", dw_col)
                  # print("Number of window is", N_parallel_window(image,kernel,dw_row,dw_col))
                  if marginal_optimizable_row(image, kernel, dw_row):
                          print(image,kernel,dw_row)
                          mmarginal_space_row = (image-dw_row) % (dw_row - kernel +1)
                          # print("marginal_space_row is",mmarginal_space_row) # 2
                          mmoX_row = mmarginal_space_row + kernel - 1 #6
                          mmoX_col = (ar / pw_ic) // mmoX_row
                          mICmX = ar // (mmoX_row * mmoX_col)
                          No_of_mmoX = math.ceil(((image-mmoX_col)/(mmoX_col - kernel +1)))+1
                          # print("marginal_window_size on rows has size", moX_row, "x", moX_col, ", and No_of_marginal_window_X is", No_of_moX)
                          print("Marginal_window_row:", moX_row, "x", moX_col, "x", mICmX)
                          print("No_of_marginal_window_row:", No_of_moX)
                  else:
                          # print("There is no marginal rows to be optimzed.")
                          No_of_mmoX =0

                  if marginal_optimizable_col(image, kernel, dw_col):
                          mmarginal_space_col = (image-dw_col) % (dw_col - kernel +1)
                          print("marginal_space_col is",mmarginal_space_col) # 1
                          mmoY_col = mmarginal_space_col + kernel - 1 #3
                          mmoY_row = (pw_row * pw_col) // mmoY_col #7
                          mICmY = ar // (mmoY_row * mmoY_col)
                          No_of_mmoY = math.ceil(((image-mmoY_row)/(mmoY_row - kernel +1)))+1
                          # print("marginal_window_size on cols has size", moY_row, "x", moY_col, ", and No_of_marginal_window_Y is", No_of_moY)
                          print("Marginal_window_column:", moY_row, "x", moY_col, "x", mICmY)
                          print("No_of_marginal_window_column:", No_of_moY)
                  else:
                          # print("There is no marginal cols to be optimzed.")
                          No_of_mmoY=0

            #               No_windows_so = N_parallel_window_so(image,kernel,so_row,so_col)
            # No_windows = ( No_windows_so + No_of_moX + No_of_moY )
                  No_window_with_marginal = N_parallel_window_so(image,kernel,dw_row,dw_col) + No_of_mmoX + No_of_mmoY
                  # print("No_window_with_marginal：",No_window_with_marginal)

                  # No_windows += optimal_N_parallel_window + No_of_mmoX + No_of_mmoY
                  if (No_window_with_marginal<= No_remaining_parallel_window) and (dw_row*dw_col * (remaining_channels) <= ar) :
                      found_max = True
                      optimal_N_parallel_window = N_parallel_window(image,kernel,dw_row,dw_col)
                      do_row = dw_row
                      do_col = dw_col
                      No_cells_do = dw_row*dw_col
                      mICt = ar // No_cells_do
                      # N_parallel_window_so(image,kernel,so_row,so_col)
                      # print("Depth-optimal window:", do_row, "x", do_col, "is better than the original PW", pw_row, pw_col)
                      print("Depth-optimal window:", do_row, "x", do_col, "x",mICt)
                      # print(optimal_N_parallel_window, "optimal_N_parallel_window")
                      No_windows += No_window_with_marginal
                      print("OVERALL Computing Cycle:", No_windows)
                      break
                  # else:
                      # print("This pair is not allowed")


      prune =1

  return No_windows

#%%
import math
# from function_1 import *
# import matplotlib.pyplot as plt
# import argparse

'''
Mapping Method
im2col, SDK, VW-SDK


28	5	16x32
28	5	32x96
14	5	16x48
14	5	24x64
14	5	24x64
14	5	32x64
14	5	32x128
7	5	32x128
7	5	28x128
'''

# Here, we define the customized layer topology
# cnn8-3
image, kernel, ic, oc, ar, ac, method = 18, 3, 32, 32, 512, 512, 'VW-SDK'

# inception-4e
# image, kernel, ic, oc, ar, ac, method = 14, 5, 32, 128, 512, 512, 'VW-SDK'

# resnet50-blk1
# image, kernel, ic, oc, ar, ac, method = 56, 3, 64, 256, 512, 512, 'VW-SDK'

# densenet40-3
# image, kernel, ic, oc, ar, ac, method = 32, 3, 48, 12, 512, 512/8, 'VW-SDK'



print("="*50)
print("INFORMATION")
print("-"*30)
print("    Array   Size = {} x {}".format(ar, ac))
print("    Image   Size = {} x {}".format(image, image))
print("    Kernel  Size = {} x {}".format(kernel, kernel))
print("    Channel Size = {} x {}".format(ic, oc))
print("-"*30)

result_vw(image, kernel, ic, oc, ar, ac, method)
pw_row, pw_col, pw_ic, pw_oc = result_vw(image, kernel, ic, oc, ar, ac, method)
print(pw_row, pw_col, pw_ic, pw_oc)

tetris_cc(image, kernel, ic, oc, ar, ac, pw_row, pw_col, pw_ic, pw_oc)

group = 2
ic = ic/group
oc = oc/group
print("="*50)
print("INFORMATION")
print("-"*30)
print("    Array   Size = {} x {}".format(ar, ac))
print("    Image   Size = {} x {}".format(image, image))
print("    Kernel  Size = {} x {}".format(kernel, kernel))
print("    Channel Size = {} x {}".format(ic, oc))
print("-"*30)
pw_row, pw_col, pw_ic, pw_oc = result_vw(image, kernel, ic, oc, ar, ac, method)

# image, kernel, ic, oc, ar, ac = 14, 5, 16, 48, 512, 256
# pw_row, pw_col, pw_ic, pw_oc = 4 , 3 , 42 , 256
print("RESULT CC")
print("IC",ic)
result = group * tetris_cc(image, kernel, ic, oc, ar, ac, pw_row, pw_col, pw_ic, pw_oc)
result