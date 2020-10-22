
import subprocess


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


async def rpninp(self, chan, nick, msg):
  if chan not in self.rpnhist:
    self.rpnhist[chan] = [0]
  try:
    for m in msg.split(' '):
        self.rpnhist[chan].append(0)
        del self.rpnhist[chan][15:]
        if isfloat(m):
          self.rpnhist[chan].insert(0, float(m))
          continue
        elif m == '+' or m == 'a':
          self.rpnhist[chan][0] = self.rpnhist[chan][0]+self.rpnhist[chan].pop(1)
        elif m == '-' or m == 's':
          self.rpnhist[chan][0] =  self.rpnhist[chan].pop(1)-self.rpnhist[chan][0]
        elif m == '\\':
          self.rpnhist[chan].insert(0,self.rpnhist[chan][0])
        elif m == '*' or m == 'x' or m == 'm':
          self.rpnhist[chan][0] =  self.rpnhist[chan].pop(1)*self.rpnhist[chan][0]

        elif m == '/' or m == 'd':
          try:
            self.rpnhist[chan][0] =  self.rpnhist[chan].pop(1)/self.rpnhist[chan][0]
          except ZeroDivisionError:
            self.rpnhist[chan][0] = float('NaN')

        elif m == '^' or m == 'e':
          self.rpnhist[chan][0] =  self.rpnhist[chan].pop(1)**self.rpnhist[chan][0]

        elif msg == 'p':
          pass # just dont do anything lol
        elif msg == 'r':
          if chan in self.rpnprint:
            await self.message(chan, '[\x036rpn\x0f] {}'.format(str(self.rpnhist[chan])))
          return
        else:
          return
  except OverflowError:
    if chan in self.rpnprint:
      await self.message(chan, '[\x036rpn\x0f] no u ur numbers are too phat')
    return
  if chan in self.rpnprint:
    await self.message(chan, '[\x036rpn\x0f] '+str(self.rpnhist[chan][0]))

async def rpntoggle(self, chan, nick, msg):
  if chan in self.rpnprint:
    self.rpnprint.remove(chan)
    await self.message(chan, '[\x036rpn\x0f] rpn outputting has been disabled')
  else:
    self.rpnprint.append(chan)
    await self.message(chan, '[\x036rpn\x0f] rpn outputting has been enabled') 

async def init(self):
  self.help['rpn'] = ['rpn <inp> - simple reverse polish notation calculator (more)', 'it has an alias of . so you can just do {}. <inp>, and if enabled it will also parse floats and functions as input. there are 4 functions, add (+|a), subtract (-|s), multiply (*|x|m), and devide (/|d), and p to print register 0'.format(self.prefix)]
  self.cmd['rpn'] = rpninp
  self.cmd['.'] = rpninp
  self.rawm['rpn'] = rpninp
  self.cmd['rt'] = rpntoggle
  self.help['rt'] = ['rt - toggle the output of rpn calculatons into the channel', 'rpn is cool']

  self.rpnhist = {}

  self.rpnprint = []
