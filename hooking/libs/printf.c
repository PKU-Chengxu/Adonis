int printf(const char* format, ...){
    char hook_buff[BUFF_SIZE];
    
    sprintf(hook_buff, "printf((%s))", format);
    int sfd = get_sfd();
    hook_log(sfd, hook_buff);


    // refer to https://code.woboq.org/userspace/glibc/stdio-common/printf.c.html
    va_list arg;
    int done;
    va_start (arg, format);
    done = vfprintf (stdout, format, arg);
    va_end (arg);

    sprintf(hook_buff, "==%d%c", done, sep);
    hook_log(sfd, hook_buff);

    return done;
}