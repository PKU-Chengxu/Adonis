
int open(const char *pathname, int flags, ...) {
    char hook_buff[BUFF_SIZE];
    // sprintf(hook_buff, "open((%s;%d))", pathname, flags);
    
    mode_t mode = 0;
    if ((flags & O_CREAT) || (flags & O_TMPFILE) == O_TMPFILE) {
        va_list ap;
		va_start(ap, flags);
		mode = va_arg(ap, mode_t);
		va_end(ap);
        // sprintf(hook_buff, "open((%s;%d;%u))", pathname, flags, mode);
    } 
    sprintf(hook_buff, "open((%s;%d;%u))", pathname, flags, mode);

    int sfd = get_sfd();
    hook_log(sfd, hook_buff);
    
    int (*unhooked_open)(const char *pathname, int flags, mode_t mode);
    int result;
    unhooked_open = dlsym(RTLD_NEXT, "open");
    result = unhooked_open(pathname, flags, mode);

    sprintf(hook_buff, "==%d%c", result, sep);
    hook_log(sfd, hook_buff);
    return result;
}