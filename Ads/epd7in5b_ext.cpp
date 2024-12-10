#include "epd7in5b_ext.h"

#include "epdif_V2.h"

void DisplayFrame(unsigned char *pbuffer, unsigned long xStart, unsigned long yStart, unsigned long Picture_Width, unsigned long Picture_Height)
// void DisplayFrame(unsigned char *pbuffer, unsigned long Block, unsigned long Picture_Width=epd.width, unsigned long Picture_Height=epd.height)
{
  // Full screen parameters
  Serial.print("Displaying ");
  Serial.print(Picture_Width);
  Serial.print(" x ");
  Serial.println(Picture_Height);
  // Black and white part
  epd.SendCommand(0x10);
  for (unsigned long j = 0; j < Picture_Height; j++) {
    for (unsigned long i = 0; i < Picture_Width / 8; i++) {
      if ((j >= yStart) && (j < yStart + Picture_Height) && (i * 8 >= xStart) && (i * 8 < xStart + Picture_Width)) {
        epd.SendData((pgm_read_byte(&(pbuffer[i - xStart / 8 + (Picture_Width) / 8 * (j - yStart)]))));
      } else {
        epd.SendData(0xff);
      }
    }
  }

  epd.SendCommand(0x12);
  // epd.DelayMs(100);
  delay(100);
  epd.WaitUntilIdle();
}

// Red part
// epd.Displaypart(image_data, xStart, yStart, Picture_Width, Picture_Height, 1);

// No need for explicit refresh as it's handled in Displaypart Block=1