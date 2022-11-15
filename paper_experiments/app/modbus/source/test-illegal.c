/*
 * Copyright © 2008-2014 Stéphane Raimbault <stephane.raimbault@gmail.com>
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <modbus.h>

#include "unit-test.h"

const int EXCEPTION_RC = 2;

enum {
    TCP,
    TCP_PI,
    RTU
};

int test_server(modbus_t *ctx, int use_backend);
int send_crafted_request(modbus_t *ctx, int function,
                         uint8_t *req, int req_size,
                         uint16_t max_value, uint16_t bytes,
                         int backend_length, int backend_offset);
int equal_dword(uint16_t *tab_reg, const uint32_t value);
int is_memory_equal(const void *s1, const void *s2, size_t size);

#define BUG_REPORT(_cond, _format, _args ...) \
    printf("\nLine %d: assertion error for '%s': " _format "\n", __LINE__, # _cond, ## _args)

#define ASSERT_TRUE(_cond, _format, __args...) {  \
    if (_cond) {                                  \
        printf("OK\n");                           \
    } else {                                      \
        BUG_REPORT(_cond, _format, ## __args);    \
        goto close;                               \
    }                                             \
};

int is_memory_equal(const void *s1, const void *s2, size_t size)
{
    return (memcmp(s1, s2, size) == 0);
}

int equal_dword(uint16_t *tab_reg, const uint32_t value) {
    return ((tab_reg[0] == (value >> 16)) && (tab_reg[1] == (value & 0xFFFF)));
}

int main(int argc, char *argv[])
{
    const int NB_REPORT_SLAVE_ID = 10;
    uint8_t *tab_rp_bits = NULL;
    uint16_t *tab_rp_registers = NULL;
    uint16_t *tab_rp_registers_bad = NULL;
    modbus_t *ctx = NULL;
    int i;
    uint8_t value;
    int nb_points;
    int rc;
    float real;
    uint32_t old_response_to_sec;
    uint32_t old_response_to_usec;
    uint32_t new_response_to_sec;
    uint32_t new_response_to_usec;
    uint32_t old_byte_to_sec;
    uint32_t old_byte_to_usec;
    int use_backend;
    int success = FALSE;
    int old_slave;

    if (argc > 1) {
        if (strcmp(argv[1], "tcp") == 0) {
            use_backend = TCP;
        } else if (strcmp(argv[1], "tcppi") == 0) {
            use_backend = TCP_PI;
        } else if (strcmp(argv[1], "rtu") == 0) {
            use_backend = RTU;
        } else {
            printf("Usage:\n  %s [tcp|tcppi|rtu] - Modbus client for unit testing\n\n", argv[0]);
            exit(1);
        }
    } else {
        /* By default */
        use_backend = TCP;
    }

    if (use_backend == TCP) {
        ctx = modbus_new_tcp("127.0.0.1", 1502);
    } else if (use_backend == TCP_PI) {
        ctx = modbus_new_tcp_pi("::1", "1502");
    } else {
        ctx = modbus_new_rtu("/dev/ttyUSB1", 115200, 'N', 8, 1);
    }
    if (ctx == NULL) {
        fprintf(stderr, "Unable to allocate libmodbus context\n");
        return -1;
    }
    modbus_set_debug(ctx, TRUE);
    modbus_set_error_recovery(ctx,
                              MODBUS_ERROR_RECOVERY_LINK |
                              MODBUS_ERROR_RECOVERY_PROTOCOL);

    if (use_backend == RTU) {
        modbus_set_slave(ctx, SERVER_ID);
    }

    modbus_get_response_timeout(ctx, &old_response_to_sec, &old_response_to_usec);
    if (modbus_connect(ctx) == -1) {
        fprintf(stderr, "Connection failed: %s\n", modbus_strerror(errno));
        modbus_free(ctx);
        return -1;
    }

    /* Allocate and initialize the memory to store the bits */
    nb_points = (UT_BITS_NB > UT_INPUT_BITS_NB) ? UT_BITS_NB : UT_INPUT_BITS_NB;
    tab_rp_bits = (uint8_t *) malloc(nb_points * sizeof(uint8_t));
    memset(tab_rp_bits, 0, nb_points * sizeof(uint8_t));

    /* Allocate and initialize the memory to store the registers */
    nb_points = (UT_REGISTERS_NB > UT_INPUT_REGISTERS_NB) ?
        UT_REGISTERS_NB : UT_INPUT_REGISTERS_NB;
    tab_rp_registers = (uint16_t *) malloc(nb_points * sizeof(uint16_t));
    memset(tab_rp_registers, 0, nb_points * sizeof(uint16_t));

    printf("** UNIT TESTING **\n");

    printf("1/1 No response timeout modification on connect: ");
    modbus_get_response_timeout(ctx, &new_response_to_sec, &new_response_to_usec);
    ASSERT_TRUE(old_response_to_sec == new_response_to_sec &&
                old_response_to_usec == new_response_to_usec, "");

    printf("\nAt this point, error messages doesn't mean the test has failed\n");

    /** ILLEGAL DATA ADDRESS **/
    printf("\nTEST ILLEGAL DATA ADDRESS:\n");

    /* The mapping begins at the defined addresses and ends at address +
     * nb_points so these addresses are not valid. */

    rc = modbus_read_bits(ctx, 0, 1, tab_rp_bits);
    printf("* modbus_read_bits (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_bits(ctx, UT_BITS_ADDRESS, UT_BITS_NB + 1, tab_rp_bits);
    printf("* modbus_read_bits (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_input_bits(ctx, 0, 1, tab_rp_bits);
    printf("* modbus_read_input_bits (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_input_bits(ctx, UT_INPUT_BITS_ADDRESS,
                                UT_INPUT_BITS_NB + 1, tab_rp_bits);
    printf("* modbus_read_input_bits (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_registers(ctx, 0, 1, tab_rp_registers);
    printf("* modbus_read_registers (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_registers(ctx, UT_REGISTERS_ADDRESS,
                               UT_REGISTERS_NB_MAX + 1, tab_rp_registers);
    printf("* modbus_read_registers (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_input_registers(ctx, 0, 1, tab_rp_registers);
    printf("* modbus_read_input_registers (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_read_input_registers(ctx, UT_INPUT_REGISTERS_ADDRESS,
                                     UT_INPUT_REGISTERS_NB + 1,
                                     tab_rp_registers);
    printf("* modbus_read_input_registers (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_bit(ctx, 0, ON);
    printf("* modbus_write_bit (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_bit(ctx, UT_BITS_ADDRESS + UT_BITS_NB, ON);
    printf("* modbus_write_bit (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_bits(ctx, 0, 1, tab_rp_bits);
    printf("* modbus_write_coils (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_bits(ctx, UT_BITS_ADDRESS + UT_BITS_NB,
                           UT_BITS_NB, tab_rp_bits);
    printf("* modbus_write_coils (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_register(ctx, 0, tab_rp_registers[0]);
    printf("* modbus_write_register (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_register(ctx, UT_REGISTERS_ADDRESS + UT_REGISTERS_NB_MAX,
                                tab_rp_registers[0]);
    printf("* modbus_write_register (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_registers(ctx, 0, 1, tab_rp_registers);
    printf("* modbus_write_registers (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_registers(ctx, UT_REGISTERS_ADDRESS + UT_REGISTERS_NB_MAX,
                                UT_REGISTERS_NB, tab_rp_registers);
    printf("* modbus_write_registers (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_mask_write_register(ctx, 0, 0xF2, 0x25);
    printf("* modbus_mask_write_registers (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_mask_write_register(ctx, UT_REGISTERS_ADDRESS + UT_REGISTERS_NB_MAX,
                                    0xF2, 0x25);
    printf("* modbus_mask_write_registers (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_and_read_registers(ctx, 0, 1, tab_rp_registers, 0, 1, tab_rp_registers);
    printf("* modbus_write_and_read_registers (0): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");

    rc = modbus_write_and_read_registers(ctx,
                                         UT_REGISTERS_ADDRESS + UT_REGISTERS_NB_MAX,
                                         UT_REGISTERS_NB, tab_rp_registers,
                                         UT_REGISTERS_ADDRESS + UT_REGISTERS_NB_MAX,
                                         UT_REGISTERS_NB, tab_rp_registers);
    printf("* modbus_write_and_read_registers (max): ");
    ASSERT_TRUE(rc == -1 && errno == EMBXILADD, "");


    printf("\nALL TESTS PASS WITH SUCCESS.\n");
    success = TRUE;

close:
    /* Free the memory */
    free(tab_rp_bits);
    free(tab_rp_registers);

    /* Close the connection */
    modbus_close(ctx);
    modbus_free(ctx);

    return (success) ? 0 : -1;
}

/* Send crafted requests to test server resilience
   and ensure proper exceptions are returned. */
int test_server(modbus_t *ctx, int use_backend)
{
    int rc;
    int i;
    /* Read requests */
    const int READ_RAW_REQ_LEN = 6;
    const int slave = (use_backend == RTU) ? SERVER_ID : MODBUS_TCP_SLAVE;
    uint8_t read_raw_req[] = {
        slave,
        /* function, address, 5 values */
        MODBUS_FC_READ_HOLDING_REGISTERS,
        UT_REGISTERS_ADDRESS >> 8, UT_REGISTERS_ADDRESS & 0xFF,
        0x0, 0x05
    };
    /* Write and read registers request */
    const int RW_RAW_REQ_LEN = 13;
    uint8_t rw_raw_req[] = {
        slave,
        /* function, addr to read, nb to read */
        MODBUS_FC_WRITE_AND_READ_REGISTERS,
        /* Read */
        UT_REGISTERS_ADDRESS >> 8, UT_REGISTERS_ADDRESS & 0xFF,
        (MODBUS_MAX_WR_READ_REGISTERS + 1) >> 8,
        (MODBUS_MAX_WR_READ_REGISTERS + 1) & 0xFF,
        /* Write */
        0, 0,
        0, 1,
        /* Write byte count */
        1 * 2,
        /* One data to write... */
        0x12, 0x34
    };
    const int WRITE_RAW_REQ_LEN = 13;
    uint8_t write_raw_req[] = {
        slave,
        /* function will be set in the loop */
        MODBUS_FC_WRITE_MULTIPLE_REGISTERS,
        /* Address */
        UT_REGISTERS_ADDRESS >> 8, UT_REGISTERS_ADDRESS & 0xFF,
        /* 3 values, 6 bytes */
        0x00, 0x03, 0x06,
        /* Dummy data to write */
        0x02, 0x2B, 0x00, 0x01, 0x00, 0x64
    };
    const int INVALID_FC = 0x42;
    const int INVALID_FC_REQ_LEN = 6;
    uint8_t invalid_fc_raw_req[] = {
        slave, 0x42, 0x00, 0x00, 0x00, 0x00
    };

    int req_length;
    uint8_t rsp[MODBUS_TCP_MAX_ADU_LENGTH];
    int tab_read_function[] = {
        MODBUS_FC_READ_COILS,
        MODBUS_FC_READ_DISCRETE_INPUTS,
        MODBUS_FC_READ_HOLDING_REGISTERS,
        MODBUS_FC_READ_INPUT_REGISTERS
    };
    int tab_read_nb_max[] = {
        MODBUS_MAX_READ_BITS + 1,
        MODBUS_MAX_READ_BITS + 1,
        MODBUS_MAX_READ_REGISTERS + 1,
        MODBUS_MAX_READ_REGISTERS + 1
    };
    int backend_length;
    int backend_offset;

    if (use_backend == RTU) {
        backend_length = 3;
        backend_offset = 1;
    } else {
        backend_length = 7;
        backend_offset = 7;
    }

    printf("\nTEST RAW REQUESTS:\n");

    uint32_t old_response_to_sec;
    uint32_t old_response_to_usec;

    /* This requests can generate flushes server side so we need a higher
     * response timeout than the server. The server uses the defined response
     * timeout to sleep before flushing.
     * The old timeouts are restored at the end.
     */
    modbus_get_response_timeout(ctx, &old_response_to_sec, &old_response_to_usec);
    modbus_set_response_timeout(ctx, 0, 600000);

    req_length = modbus_send_raw_request(ctx, read_raw_req, READ_RAW_REQ_LEN);
    printf("* modbus_send_raw_request: ");
    ASSERT_TRUE(req_length == (backend_length + 5), "FAILED (%d)\n", req_length);

    printf("* modbus_receive_confirmation: ");
    rc = modbus_receive_confirmation(ctx, rsp);
    ASSERT_TRUE(rc == (backend_length + 12), "FAILED (%d)\n", rc);

    /* Try to read more values than a response could hold for all data
       types. */
    for (i=0; i<4; i++) {
        rc = send_crafted_request(ctx, tab_read_function[i],
                                  read_raw_req, READ_RAW_REQ_LEN,
                                  tab_read_nb_max[i], 0,
                                  backend_length, backend_offset);
        if (rc == -1)
            goto close;
    }

    rc = send_crafted_request(ctx, MODBUS_FC_WRITE_AND_READ_REGISTERS,
                              rw_raw_req, RW_RAW_REQ_LEN,
                              MODBUS_MAX_WR_READ_REGISTERS + 1, 0,
                              backend_length, backend_offset);
    if (rc == -1)
        goto close;

    rc = send_crafted_request(ctx, MODBUS_FC_WRITE_MULTIPLE_REGISTERS,
                              write_raw_req, WRITE_RAW_REQ_LEN,
                              MODBUS_MAX_WRITE_REGISTERS + 1, 6,
                              backend_length, backend_offset);
    if (rc == -1)
        goto close;

    rc = send_crafted_request(ctx, MODBUS_FC_WRITE_MULTIPLE_COILS,
                              write_raw_req, WRITE_RAW_REQ_LEN,
                              MODBUS_MAX_WRITE_BITS + 1, 6,
                              backend_length, backend_offset);
    if (rc == -1)
        goto close;

    /* Modbus write multiple registers with large number of values but a set a
       small number of bytes in requests (not nb * 2 as usual). */
    rc = send_crafted_request(ctx, MODBUS_FC_WRITE_MULTIPLE_REGISTERS,
                              write_raw_req, WRITE_RAW_REQ_LEN,
                              MODBUS_MAX_WRITE_REGISTERS, 6,
                              backend_length, backend_offset);
    if (rc == -1)
        goto close;

    rc = send_crafted_request(ctx, MODBUS_FC_WRITE_MULTIPLE_COILS,
                              write_raw_req, WRITE_RAW_REQ_LEN,
                              MODBUS_MAX_WRITE_BITS, 6,
                              backend_length, backend_offset);
    if (rc == -1)
        goto close;

    /* Test invalid function code */
    modbus_send_raw_request(ctx, invalid_fc_raw_req, INVALID_FC_REQ_LEN * sizeof(uint8_t));
    rc = modbus_receive_confirmation(ctx, rsp);
    printf("Return an exception on unknown function code: ");
    ASSERT_TRUE(rc == (backend_length + EXCEPTION_RC) &&
                rsp[backend_offset] == (0x80 + INVALID_FC), "")

    modbus_set_response_timeout(ctx, old_response_to_sec, old_response_to_usec);
    return 0;
close:
    modbus_set_response_timeout(ctx, old_response_to_sec, old_response_to_usec);
    return -1;
}


int send_crafted_request(modbus_t *ctx, int function,
                         uint8_t *req, int req_len,
                         uint16_t max_value, uint16_t bytes,
                         int backend_length, int backend_offset)
{
    uint8_t rsp[MODBUS_TCP_MAX_ADU_LENGTH];
    int j;

    for (j=0; j<2; j++) {
        int rc;

        req[1] = function;
        if (j == 0) {
            /* Try to read or write zero values on first iteration */
            req[4] = 0x00;
            req[5] = 0x00;
            if (bytes) {
                /* Write query */
                req[6] = 0x00;
            }
        } else {
            /* Try to read or write max values + 1 on second iteration */
            req[4] = (max_value >> 8) & 0xFF;
            req[5] = max_value & 0xFF;
            if (bytes) {
                /* Write query (nb values * 2 to convert in bytes for registers) */
                req[6] = bytes;
            }
        }

        modbus_send_raw_request(ctx, req, req_len * sizeof(uint8_t));
        if (j == 0) {
            printf("* try function 0x%X: %s 0 values: ", function, bytes ? "write": "read");
        } else {
            printf("* try function 0x%X: %s %d values: ", function, bytes ? "write": "read",
                   max_value);
        }
        rc = modbus_receive_confirmation(ctx, rsp);
        ASSERT_TRUE(rc == (backend_length + EXCEPTION_RC) &&
                    rsp[backend_offset] == (0x80 + function) &&
                    rsp[backend_offset + 1] == MODBUS_EXCEPTION_ILLEGAL_DATA_VALUE, "");
    }
    return 0;
close:
    return -1;
}
