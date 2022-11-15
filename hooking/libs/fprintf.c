int fprintf(FILE* stream, const char* format, ...){
    char hook_buff[BUFF_SIZE];
    
    sprintf(hook_buff, "fprintf((_;%s))", format);
    int sfd = get_sfd();
    hook_log(sfd, hook_buff);


    // refer to https://code.woboq.org/userspace/glibc/stdio-common/fprintf.c.html
    va_list arg;
    int done;
    va_start(arg, format);
    done = vfprintf(stream, format, arg);
    va_end (arg);

    sprintf(hook_buff, "==%d", done);
    sprintf(hook_buff + len(hook_buff), "%c", sep);
    hook_log(sfd, hook_buff);

    return done;
}