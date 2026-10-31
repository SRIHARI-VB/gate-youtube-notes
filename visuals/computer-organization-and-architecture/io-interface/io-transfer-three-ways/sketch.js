/* One 500-byte block, three ways to move it, for the I/O Interface topic.

   The picture is fixed for the whole lesson:

     500 bytes from a device to memory
     the device produces one byte every 200 cycles, so the transfer spans 100,000 cycles
     programmed I/O: the CPU is in the status loop for all 100,000 cycles
     interrupt-driven: 2 + 500 x 7 = 3502 cycles of CPU time
     DMA: 20 + 500 x 2 = 1020 cycles of CPU time, in cycle stealing or burst mode

   Every figure is listed in lesson.json and recomputed in scripts/validate.py
   (check_io_interface), not derived from this file. */

var BYTES = 500;
var DEV = 200;              // device cycles per byte
var SPAN = BYTES * DEV;     // 100000 cycles of device time
var ISR_INIT = 2, ISR_PER = 7, ISR = ISR_INIT + BYTES * ISR_PER;      // 3502
var DMA_INIT = 20, DMA_PER = 2, DMA_XFER = BYTES * DMA_PER;           // 1000
var DMA_TOTAL = DMA_INIT + DMA_XFER;                                  // 1020
var SPEEDUP = ISR / DMA_TOTAL;                                        // 3.433

var C_CPU = [198, 216, 240];   // CPU busy: blue
var C_IDLE = [226, 232, 238];  // CPU free: grey
var C_BUS = [246, 214, 156];   // bus held by the controller: amber
var C_DEV = [214, 232, 214];   // device working: green

function ink() {
  background(255);
  stroke(210);
  strokeWeight(1);
  fill(40);
}

function head(t) { fill(28); textSize(17); textStyle(BOLD); textAlign(LEFT, TOP); text(t, 22, 18); textStyle(NORMAL); }

function note(t, y) { fill(74, 82, 96); textSize(13); textAlign(LEFT, TOP); text(t, 22, y); }

function label(t, x, y) { fill(60); textSize(12); textAlign(LEFT, TOP); text(t, x, y); }

/* A horizontal bar of total width w, from cycle 0 to SPAN, with the given segments.
   Each segment is {from, to, colour, tag}. */
function bar(x, y, w, h, segs) {
  stroke(205);
  strokeWeight(1);
  noFill();
  rect(x, y, w, h);
  for (var i = 0; i < segs.length; i++) {
    var s = segs[i];
    var x0 = x + (s.from / SPAN) * w;
    var x1 = x + (s.to / SPAN) * w;
    if (x1 - x0 < 1) { x1 = x0 + 1; }
    noStroke();
    fill(s.colour[0], s.colour[1], s.colour[2]);
    rect(x0, y, x1 - x0, h);
    if (s.tag) { label(s.tag, x0 + 2, y + h + 4); }
    noStroke();
  }
  stroke(205);
}

/* The small "bus cycles" strip used for the two DMA modes: 1000 cycles of bus time,
   drawn as the blocks the controller takes. */
function busStrip(x, y, w, h, chunks) {
  stroke(205); strokeWeight(1); noFill(); rect(x, y, w, h);
  for (var i = 0; i < chunks.length; i++) {
    var c = chunks[i];
    var x0 = x + (c.from / DMA_XFER) * w;
    var x1 = x + (c.to / DMA_XFER) * w;
    if (x1 - x0 < 1) { x1 = x0 + 1; }
    noStroke(); fill(C_BUS[0], C_BUS[1], C_BUS[2]); rect(x0, y, x1 - x0, h); noStroke();
  }
  stroke(205);
}

window.LESSON = {
  steps: [
    {
      duration: 5200,
      caption: 'The cast, and the one number everything is measured against. Five hundred bytes must move from a device into memory, and the device delivers one byte every 200 cycles, so the transfer occupies 100,000 cycles of device time. Nothing the CPU does can make the device faster. The only question is what the CPU is doing during those 100,000 cycles.',
      draw: function (p, w, h) {
        ink();
        head('500 bytes, 200 cycles per byte: a 100,000-cycle transfer');
        var bx = 22, by = 58, bw = w - 44, bh = 26;
        bar(bx, by, bw, bh, [{ from: 0, to: SPAN, colour: C_DEV, tag: 'device working, 0 to 100,000 cycles' }]);
        label('device', bx + 4, by - 18);
        note('The device is the slow party. Every scheme below moves the same 500 bytes in the same', 132);
        note('100,000 cycles of device time; they differ only in how much of that time the CPU spends.', 154);
        note('Device time: 500 x 200 = 100,000 cycles.', 196);
      }
    },
    {
      duration: 5600,
      caption: 'Programmed I/O. The CPU asks the status register whether a byte is ready, finds it is not, asks again, and stays in that loop until the device has something. So the CPU is busy for the entire 100,000 cycles, and the transfer of 500 bytes costs the CPU 100,000 cycles of work of which almost all is waiting. This is the busy waiting that GATE CSE 2024 Set 1 Q.15 calls the worst CPU utilisation of the three.',
      draw: function (p, w, h) {
        ink();
        head('Programmed I/O: the CPU is in the loop for all 100,000 cycles');
        var bx = 22, by = 58, bw = w - 44, bh = 26;
        bar(bx, by, bw, bh, [{ from: 0, to: SPAN, colour: C_CPU, tag: 'CPU busy: poll, test, poll, test' }]);
        note('Cost to the CPU: 100,000 cycles. Cost to the device: none, it was never waiting.', 132);
        note('The loop reads the status register, tests the ready bit, and branches back - repeatedly.', 154);
        note('Nothing else can run, because the CPU is executing the loop, not idling.', 176);
      }
    },
    {
      duration: 5600,
      caption: 'Interrupt-driven I/O. Now the interface watches the device and the CPU is free between bytes; it is entered only when a byte is ready. The grey is CPU time that belongs to other work. But each entry costs a service routine that loads the byte, stores it, bumps the address, decrements the count and branches: 7 cycles per byte, so 3502 cycles of CPU time for the block.',
      draw: function (p, w, h) {
        ink();
        head('Interrupt-driven: the CPU is free between bytes');
        var bx = 22, by = 58, bw = w - 44, bh = 26;
        var segs = [{ from: 0, to: SPAN, colour: C_IDLE, tag: 'CPU free for other work' }];
        for (var i = 0; i < 40; i++) {
          var at = (i * SPAN) / 40;
          segs.push({ from: at, to: at + (7 * BYTES * 0) + 120, colour: C_CPU });
        }
        bar(bx, by, bw, bh, segs);
        note('Each thin blue stripe is one interrupt and one service routine, 7 cycles of work.', 132);
        note('Cost to the CPU: 2 + 500 x 7 = 3502 cycles, spread across the transfer.', 154);
        note('The wait is gone; the per-byte work is not.', 176);
      }
    },
    {
      duration: 5400,
      caption: 'The service routine counted. Two cycles to initialise the address register and the count, then seven cycles per byte: a two-cycle load from the device, a two-cycle store to memory, and one cycle each to increment the address, decrement the count and branch. Five hundred bytes therefore cost 2 + 3500 = 3502 cycles. This is the interrupt-driven side of GATE CSE 2011 Q.28.',
      draw: function (p, w, h) {
        ink();
        head('The service loop: 2 + 500 x 7 = 3502 cycles');
        var rows = [
          ['load a byte from the device', '2 cycles'],
          ['store it at the address register', '2 cycles'],
          ['increment the address register', '1 cycle'],
          ['decrement the count', '1 cycle'],
          ['branch if the count is not zero', '1 cycle'],
          ['per byte', '7 cycles'],
          ['initialise address and count, once', '2 cycles'],
          ['500 bytes in total', '3502 cycles']
        ];
        for (var i = 0; i < rows.length; i++) {
          var y = 58 + i * 26;
          label(rows[i][0], 22, y);
          label(rows[i][1], 400, y);
          if (i === 5 || i === 7) { stroke(200); line(22, y + 20, 470, y + 20); }
        }
        note('Every one of these cycles is CPU time, paid once per byte, whatever the device does.', 288);
      }
    },
    {
      duration: 5400,
      caption: 'DMA setup. The CPU writes three registers of the DMA controller - the memory start address, the byte count of 500, and a control word for direction and mode - and then leaves the bus. Twenty cycles of CPU time in total, and the CPU is out of the data path from here on. Compare that with the 3502 cycles the service routine needed.',
      draw: function (p, w, h) {
        ink();
        head('DMA setup: 20 cycles, then the CPU steps off the bus');
        var rows = [
          ['memory address register', 'start of the buffer'],
          ['count register', '500 bytes'],
          ['control / status register', 'device to memory, mode, interrupt enable']
        ];
        for (var i = 0; i < rows.length; i++) {
          var y = 60 + i * 40;
          noStroke(); fill(198, 216, 240); rect(22, y, 8, 16); noStroke();
          label(rows[i][0], 40, y + 2);
          label(rows[i][1], 300, y + 2);
        }
        note('The controller now owns the address and the count, so it can generate them itself.', 210);
        note('CPU cost so far: 20 cycles. Data moved so far: none.', 232);
        note('At the end the controller raises ONE interrupt, not one per byte.', 254);
      }
    },
    {
      duration: 5800,
      caption: 'Cycle stealing. The controller asks for the bus, the CPU finishes the cycle it is on and grants it, the controller moves two cycles worth of data - one byte - and hands the bus straight back. It repeats that 500 times. The CPU keeps running between the stolen cycles, so it is slowed, not stopped, which is why cycle stealing is the mode for a machine that must stay responsive.',
      draw: function (p, w, h) {
        ink();
        head('Cycle stealing: one byte per stolen turn, the bus handed back');
        var chunks = [];
        for (var i = 0; i < 20; i++) {
          var at = (i * DMA_XFER) / 20;
          chunks.push({ from: at, to: at + DMA_XFER / 40 });
        }
        busStrip(22, 58, w - 44, 26, chunks);
        note('Each amber sliver is one stolen turn: 2 cycles of bus time carrying 1 byte.', 132);
        note('500 turns x 2 cycles = 1000 cycles of bus time, in 500 separate pieces.', 154);
        note('The CPU executes between the slivers. Its throughput drops by the fraction stolen.', 176);
        note('CPU cost: 20 cycles of setup plus a completion interrupt, and nothing per byte.', 198);
      }
    },
    {
      duration: 5600,
      caption: 'Burst mode on the same controller. The bus is granted once and held until all 500 bytes have moved: the same 1000 cycles of bus time, but contiguous. Throughput is the highest of any mode because there is no handshake per word, and the price is that the CPU cannot use the bus at all for those 1000 cycles. That is the trade GATE CSE 2024 Set 1 Q.15 states as true: burst has the higher throughput.',
      draw: function (p, w, h) {
        ink();
        head('Burst: the whole 1000 cycles of bus time in one piece');
        busStrip(22, 58, w - 44, 26, [{ from: 0, to: DMA_XFER }]);
        note('One request, one grant, 1000 cycles held, one release.', 132);
        note('No per-word handshake, so this is the highest-throughput mode.', 154);
        note('The CPU is stalled for the whole block - the cost that cycle stealing avoids.', 176);
        note('Both modes move the same 1000 cycles of data; only the sharing changes.', 198);
      }
    },
    {
      duration: 6000,
      caption: 'The three schemes on one scale. Programmed I/O costs the CPU the whole 100,000 cycles. Interrupt-driven I/O costs 3502. DMA costs 1020, of which 20 are setup and the rest is bus time taken from the CPU. The speed-up of DMA over the interrupt routine is 3502 / 1020 = 3.43, which is the answer to GATE CSE 2011 Q.28 rounded to 3.4 - and the reason is that the CPU no longer touches a single byte.',
      draw: function (p, w, h) {
        ink();
        head('One block, three costs, on the same scale');
        var rows = [
          ['programmed I/O', 100000, C_CPU, '100,000 cycles - the whole transfer'],
          ['interrupt-driven', 3502, C_CPU, '3,502 cycles - 7 per byte'],
          ['DMA', 1020, C_BUS, '1,020 cycles - 20 setup plus 1000 of bus time']
        ];
        var bx = 150, bw = w - 172;
        for (var i = 0; i < rows.length; i++) {
          var y = 56 + i * 58;
          label(rows[i][0], 22, y + 4);
          stroke(205); strokeWeight(1); noFill(); rect(bx, y, bw, 22);
          var x1 = bx + (rows[i][1] / SPAN) * bw;
          if (x1 - bx < 2) { x1 = bx + 2; }
          noStroke(); fill(rows[i][2][0], rows[i][2][1], rows[i][2][2]); rect(bx, y, x1 - bx, 22); noStroke();
          label(rows[i][3], bx, y + 26);
        }
        note('Speed-up of DMA over the interrupt routine: 3502 / 1020 = 3.43, that is 3.4.', 250);
        note('The bars are drawn to the same scale, so the 100,000-cycle bar is the whole axis.', 272);
      }
    }
  ]
};
