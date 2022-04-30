#include <stdio.h>
#include <zint.h>
#include <stdlib.h>

const char FOREGROUND = '1';
const char BACKGROUND = '2';

char * last_result = NULL;

char * encode_2d_symbol(struct zint_symbol* symbol, unsigned char * data);
char * encode_aztec_code(unsigned char * data);
char * encode_qr_code(unsigned char * data);

char * encode_2d_symbol(struct zint_symbol* symbol, unsigned char * data)
{
    symbol->input_mode = DATA_MODE; // DATA_MODE | UNICODE_MODE
    symbol->output_options |= OUT_BUFFER_INTERMEDIATE;

    ZBarcode_Encode_and_Buffer(symbol, data, 0, 0);

    unsigned amount_of_rows = symbol->rows;
    unsigned amount_of_modules = (amount_of_rows * amount_of_rows) + 1;
    unsigned module_size = symbol->bitmap_width / symbol->width;

    char* modules = malloc(amount_of_modules * sizeof(char));

    unsigned bitmap_index = 0;
    unsigned modules_index = 0;
    for (int row = 0; row < symbol->height; row++)
    {
        for (int column = 0; column < symbol->width; column++)
        {
            char module = symbol->bitmap[bitmap_index] == FOREGROUND?
                FOREGROUND : BACKGROUND;

            modules[modules_index] = module;

            bitmap_index += module_size;
            modules_index++;
        }

        bitmap_index += symbol->width * module_size;
    }

    modules[amount_of_modules - 1] = '\0';

    return modules;
}

char * encode_aztec_code(unsigned char * data)
{
    struct zint_symbol* symbol;

    symbol = ZBarcode_Create();
    symbol->symbology = BARCODE_AZTEC;
    last_result = encode_2d_symbol(symbol, data);
    ZBarcode_Delete(symbol);

    return last_result;
}

char * encode_qr_code(unsigned char * data)
{
    struct zint_symbol* symbol;

    symbol = ZBarcode_Create();
    symbol->symbology = BARCODE_QRCODE;
    symbol->option_1 = 1; // Error Correction Level L=1 M=2 Q=3 H=4
    last_result = encode_2d_symbol(symbol, data);
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
