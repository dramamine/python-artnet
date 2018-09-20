import logging

import time

from artnet import dmx, fixtures, rig

# set up test fixtures
r = rig.get_default_rig()
g = r.groups['one']

log = logging.getLogger(__name__)


row_a = [0, 1, 2, 3, 4, 5, 6, 7]
row_b = [13, 12, 11, 10, 9, 8]
row_c = [14, 15, 16, 17, 18]
row_d = [22, 21, 20, 19]
row_e = [23, 24, 25]
row_f = [27, 26]
row_g = [28]

rows = [row_a, row_b, row_c, row_d, row_e, row_f, row_g]

frame = [None] * 87

eight_colors = [
  '#ff0000',
  '#00ff00',
  '#0000ff',
  '#ffff00',
  '#00ffff',
  '#ff00ff',
  '#dddddd',
  '#9900ff'
]

def hex_to_rgb(value):
  value = value.lstrip('#')
  lv = len(value)
  return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))


def set_color(frame, idx, color, intensity = 1):
  r_idx = idx * 3;
  g_idx = idx * 3 + 1;
  b_idx = idx * 3 + 2;
  r, b, g = hex_to_rgb(str(color))
  frame[r_idx] = r
  frame[g_idx] = g
  frame[b_idx] = b
  return frame

def pattern_generator(clock):
  frame = [None] * 87
  for i, row in enumerate(rows):
    for j, addr in enumerate(row):
      frame = set_color(frame, addr, eight_colors[i], 1)
  return frame


def main(config, controller=None):
  log.info("Running script %s" % __name__)
  q = controller or dmx.Controller(config.get('base', 'address'), bpm=240, nodaemon=False)

  q.add(pattern_generator(q.get_clock()))


  # g.setIntensity(255)
  # g.setColor('#ffffff')

  # g[0].setColor('#ff0000')
  # g[1].setColor('#00ff00')
  # g[2].setColor('#0000ff')
  # g[3].setColor('#ff00ff')

  # from artnet.dmx import patterns
  # q.add(patterns.rotate(q.get_clock(), g))

  if not controller:
    q.start()
