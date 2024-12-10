#include "epd7in5b_V2.h"


extern EpdV2 epd;

void DisplayFrame(unsigned char* pbuffer, unsigned long xStart = 0, unsigned long yStart = 0, unsigned long Picture_Width = epd.width, unsigned long Picture_Height = epd.height);
void DisplayQuarterFrame(unsigned char* image_data);
