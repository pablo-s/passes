#include <stdio.h>
#include <zint.h>
#include <stdlib.h>
#include <string.h>

const char FOREGROUND = '1';
const char BACKGROUND = '2';
char * last_result = NULL;

enum BarcodeType
{
    AZTEC = 0,
    CODE128,
    PDF417,
    QRCODE
};

char * encode_2d_symbol(struct zint_symbol* symbol, unsigned char * data, unsigned data_length);
char * encode_barcode(unsigned char * data, unsigned data_length, unsigned symbology, unsigned * out_width, unsigned * out_height);

char * encode_2d_symbol(struct zint_symbol* symbol, unsigned char * data, unsigned data_length)
{
    symbol->input_mode = DATA_MODE; // DATA_MODE | UNICODE_MODE
    symbol->output_options |= OUT_BUFFER_INTERMEDIATE;

    ZBarcode_Encode_and_Buffer(symbol, data, data_length, 0);
    unsigned amount_of_modules = (symbol->bitmap_height * symbol->bitmap_width) + 1;
    char* modules = malloc(amount_of_modules * sizeof(char));
    memcpy(modules, symbol->bitmap, amount_of_modules - 1);
    modules[amount_of_modules - 1] = '\0';

    return modules;
}

char * encode_barcode(unsigned char * data,
                      unsigned data_length,
                      unsigned symbology,
                      unsigned * out_width,
                      unsigned * out_height)
{
    struct zint_symbol* symbol;

    symbol = ZBarcode_Create();

    switch (symbology)
    {
        case AZTEC:
            symbol->symbology = BARCODE_AZTEC;
            break;

        case CODE128:
            symbol->symbology = BARCODE_CODE128;
            break;

        case PDF417:
            symbol->symbology = BARCODE_PDF417;
            break;

        case QRCODE:
            symbol->symbology = BARCODE_QRCODE;
            symbol->option_1 = 1; // Error Correction Level L=1 M=2 Q=3 H=4
            break;
    }

    last_result = encode_2d_symbol(symbol, data, data_length);
    *out_width = symbol->bitmap_width;
    *out_height = symbol->bitmap_height;

    ZBarcode_Delete(symbol);

    return last_result;
}

void free_last_result()
{
    if (last_result == NULL)
    {
        return;
    }

    free(last_result);
    last_result = NULL;
}
