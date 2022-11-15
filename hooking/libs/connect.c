int connect(int fd, __CONST_SOCKADDR_ARG addr, socklen_t arg_len)
{
    
    char hook_buff[BUFF_SIZE];
    sprintf(hook_buff, "connect((%d;%c;%c))", fd, '_', '_');
    int sfd = get_sfd();
    hook_log(sfd, hook_buff);

    
    int (*old_connect)(int fd, __CONST_SOCKADDR_ARG addr, socklen_t arg_len);
    int result;
    old_connect = dlsym(RTLD_NEXT, "connect");
    result = old_connect(fd, addr, arg_len);

    
    sprintf(hook_buff, "==%d", result);
    sprintf(hook_buff + len(hook_buff), "%c", sep);
    hook_log(sfd, hook_buff);

    return result;

}

