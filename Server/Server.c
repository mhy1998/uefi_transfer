//write by meihaoyan
#include <Base.h>
#include <Uefi.h>
#include <Library/UefiLib.h>
#include <AmiCompatibilityPkg/Include/AmiLib.h>
#include <AmiDxeLib.h>
#include <Library/BaseLib.h>
#include <Library/PcdLib.h>
#include <Library/UefiRuntimeServicesTableLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiApplicationEntryPoint.h>
#include <Library/DebugLib.h>
#include <Library/PrintLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/ShellLib.h>
#include <Library/TimerLib.h>
#include <Library/NetLib.h>
#include <Protocol/SimpleTextOut.h>
#include <Protocol/SimpleTextIn.h>
#include <Protocol/Dhcp4.h>
#include <Protocol/Tcp4.h>
#include <Protocol/ServiceBinding.h>
#include <Protocol/PciIo.h>
#include <Protocol/DevicePath.h>
#include <Protocol/BlockIo.h>
#include <Protocol/DevicePathToText.h>
#include <Protocol/DevicePathFromText.h>


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define MAX_FILENAME_SIZE 256
#define MAX_BUFFER_SIZE 1024


#define IP_TO_STR(ip_struct, ip_str) \
    inet_ntop(AF_INET, &(ip_struct).sin_addr, ip_str, INET_ADDRSTRLEN)

#define CHAR8_TO_CHAR16(char8,char16,len) \
        for (int i = 0; i < len; ++i) { \
        char16[i] = (CHAR16)char8[i]; \
    } \
    char16[len] = '\0'


void reverse(char str[], int length) {
    int start = 0;
    int end = length - 1;
    while (start < end) {
        char temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }
}

void int_to_str(int num, char *str) {
    int i = 0;
    int isNegative = 0;

    // 处理负数
    if (num < 0) {
        isNegative = 1;
        num = -num;
    }

    // 将数字逐位转换为字符，并存储到数组中
    do {
        str[i++] = num % 10 + '0';
        num /= 10;
    } while (num > 0);

    // 如果是负数，在字符串末尾添加负号
    if (isNegative)
        str[i++] = '-';

    // 将字符数组反转
    int start = 0;
    int end = i - 1;
    while (start < end) {
        char temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }

    // 添加字符串结束符
    str[i] = '\0';
}

VOID UpdateProgressBar(
    IN UINT8  Progress
)
{
    // 0: '['
    // 1~50: '#'
    // 51: ']'
    // 52: Null-terminate the string
    CHAR16 ProgressBar[53];

    ProgressBar[0] = L'[';
    for (UINT8 i = 1; i <= 50; i++) {
        if (i <= Progress / 2) {
            ProgressBar[i] = L'#';
        } else {
            ProgressBar[i] = L'-';
        }
    }
    ProgressBar[51] = L']';
    ProgressBar[52] = L'\0';

    // Print progress bar
    Print(L"\rProgress: %s %d%%", ProgressBar, Progress);
}

VOID
EFIAPI
SaveFileToDisk (
  IN  UINTN               BufferSize,
  IN  VOID                *Buffer,
  IN  CHAR16              *filename16
  )
{
  EFI_STATUS           Status;
  SHELL_FILE_HANDLE    FileHandle;
  EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *mTextOut;
    Status = gBS->LocateProtocol (&gEfiSimpleTextOutProtocolGuid, NULL, (VOID **) &mTextOut);
    if (EFI_ERROR (Status)) {
    Print(L"Couldn't open Text Output Protocol: %r\n", Status);
    return ;
    }
  mTextOut->OutputString (mTextOut, L"Save file...\r\n");

  Status = ShellOpenFileByName (filename16, &FileHandle, EFI_FILE_MODE_READ | EFI_FILE_MODE_WRITE | EFI_FILE_MODE_CREATE, 0);
  if (EFI_ERROR (Status)) {
    mTextOut->OutputString (mTextOut, L"ERROR: Open file\n");
    FreePool (Buffer);
    return;
  }

  Status = ShellWriteFile (FileHandle, &BufferSize, Buffer);
  if (EFI_ERROR (Status)) {
    mTextOut->OutputString (mTextOut, L"ERROR: Write file\n");
    FreePool (Buffer);
    ShellCloseFile (&FileHandle);
    return;
  }

  ShellCloseFile (&FileHandle);
  mTextOut->OutputString (mTextOut, L"Save file completed.\r\n");
}


VOID CreateServerApp(VOID){
    int serv_sock;
    int clnt_sock;


    struct sockaddr_in serv_addr;
    struct sockaddr_in clnt_addr;
    socklen_t clnt_addr_size;

    serv_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(serv_sock == -1)
    {
      Print(L"server start failed, end server\n");
      goto End;
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(4000);

    if(bind(serv_sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1)
    {
      Print(L"server start failed, end server\n");
      goto End;
    }

    if(listen(serv_sock, 5) == -1)
    {
      Print(L"server start failed, end server\n");
      goto End;
    }
    
    Print(L"Waiting for client to connect...\n");

    clnt_addr_size = sizeof(clnt_addr);
    clnt_sock = accept(serv_sock, (struct sockaddr*)&clnt_addr, &clnt_addr_size);
    if(clnt_sock == -1)
    {
      Print(L"fail to accept client link ,end server\n");
      goto End;
    }

    Print(L"Client connected.\n");

    wchar_t ip16[INET_ADDRSTRLEN];
    char ip[INET_ADDRSTRLEN];
    char *ip_str;
    ip_str = inet_ntop(AF_INET, &clnt_addr, ip, INET_ADDRSTRLEN);

    if (ip_str != NULL) {
        size_t i;
        for (i = 0; ip_str[i] != '\0'; ++i) {
            ip16[i] = (wchar_t)ip_str[i];
        }
        ip16[i] = L'\0';
        Print(L"IP Address: %s\n", ip16);
    }


while (1)
{
  UINTN       Index =0;
  EFI_INPUT_KEY  Key = {0};
  char filename[MAX_FILENAME_SIZE]={0};
  UINT8 *buffer=NULL;
  UINT8 *FileBuffer = NULL;
  char file_size[MAX_FILENAME_SIZE]={0};
  CHAR16      FileNameBuffer[200];

  Print(L"1. enter r to receive client message or file\n");
  Print(L"2. enter s to send file to client\n");
  gBS->WaitForEvent(1, &gST->ConIn->WaitForKey, &Index);
  gST->ConIn->ReadKeyStroke(gST->ConIn, &Key);
  if (Key.UnicodeChar == 'r')
  {
    {
        Print(L"Accepting client Message......\n");
        //1.read filename
        int filename_len = read(clnt_sock, filename, MAX_FILENAME_SIZE);
        if (filename_len <= 0){
          Print(L"get filename fail,end server");
          goto End;
        }

        filename[filename_len] = '\0';
        Print(L"filename_len:%d\n",filename_len);

        CHAR16 filename16[128];
        for (int i = 0; i < filename_len; ++i) {
            filename16[i] = (CHAR16)filename[i]; 
        }
        filename16[filename_len] = '\0';

        Print(L"filename16:%s\n",filename16);

        //2.read filensize
        int file_size_len = read(clnt_sock, file_size, MAX_FILENAME_SIZE);
        if (file_size_len <= 0){
          Print(L"get filesize fail,end server");
          goto End;
        }
        int filensize = atoi(file_size);

        Print(L"Received file size from client: 0x%x bytes\n",filensize);

        //3.read filendata
        UINT64 total_recv = 0;
        UINT64 recv_size;
        
        FileBuffer = (UINT8 *)AllocateZeroPool (filensize*sizeof(UINT8));
        //
        while (1) {
            if (filensize <= MAX_BUFFER_SIZE)//filesize <= 1024 byte
            {
              buffer = (UINT8 *)AllocateZeroPool(MAX_BUFFER_SIZE*sizeof(UINT8));
              recv_size = (UINT64)read(clnt_sock, buffer, filensize);
              total_recv += recv_size;
              CopyMem (FileBuffer, buffer, recv_size);
              break;
            }
            //filesize > 1024 byte
            buffer = (UINT8 *)AllocateZeroPool(MAX_BUFFER_SIZE*sizeof(UINT8));
            recv_size = (UINT64)read(clnt_sock, buffer, MAX_BUFFER_SIZE);

            UpdateProgressBar((total_recv * 100) / filensize);
              if (recv_size <= 0){
                Print(L"get file fail,end server\n");
                goto End;
              }

            CopyMem (FileBuffer+total_recv, buffer,recv_size);
            total_recv += recv_size;
            if (total_recv == filensize)
            {
              break;
            }
            
            if (total_recv + MAX_BUFFER_SIZE > filensize)
            {
              buffer = (UINT8 *)AllocateZeroPool((filensize-total_recv)*sizeof(UINT8));
              recv_size = (UINT64)read(clnt_sock, buffer, filensize-total_recv);
              CopyMem (FileBuffer+total_recv, buffer,recv_size);
              total_recv += recv_size;
              UpdateProgressBar((total_recv * 100) / filensize);
              break;
            }
        }
        gBS->FreePool((VOID*)buffer);
        Print(L"\ntotal_recv 0x%x\n",total_recv);
        SaveFileToDisk (total_recv, FileBuffer, filename16);
        Print(L"File received successfully.\n");
    }
  }
  if (Key.UnicodeChar == 's')
  {
    int keynum = 0;
    Print(L"Please input file name: Enter end\n");
    do {
      gBS->WaitForEvent(1, &gST->ConIn->WaitForKey, &Index);
      gST->ConIn->ReadKeyStroke(gST->ConIn, &Key);
      // if (Key.UnicodeChar == CHAR_BACKSPACE) {
      //   if (keynum > 0) {
      //     FileNameBuffer[keynum] = 0;
      //     keynum--;
      //   }
      // }
      // 如果输入的是Enter键，跳出循环
      if (Key.UnicodeChar == CHAR_CARRIAGE_RETURN) {
        break;
      }
      if (((Key.UnicodeChar >= 'a') && (Key.UnicodeChar <= 'z'))
      ||((Key.UnicodeChar >= 'A') && (Key.UnicodeChar <= 'Z'))
      ||(Key.UnicodeChar == '.')
      ||((Key.UnicodeChar >= '0') && (Key.UnicodeChar <= '9')))
      {
        FileNameBuffer[keynum] = Key.UnicodeChar;
        keynum++;
        Print(L"%c", Key.UnicodeChar);
      }
    } while (TRUE);


    FileNameBuffer[keynum] = L'\0';


    Print(L"\nYou have entered: %s\n", FileNameBuffer);
    

    SHELL_FILE_HANDLE    FileHandle;
    EFI_STATUS           Status;
    UINT64          Intermediate;
    CHAR16          *Data;

    Status = ShellFileExists (FileNameBuffer);
    if (EFI_ERROR (Status)) {
      Print(L"ERROR: %s is not exist.\n",FileNameBuffer);
      goto Xun;
    }
    Status = ShellOpenFileByName (FileNameBuffer, &FileHandle, EFI_FILE_MODE_READ | EFI_FILE_MODE_WRITE | EFI_FILE_MODE_CREATE, 0);
    if (EFI_ERROR (Status)) {
      Print(L"ERROR: Open %s failed.\n",FileNameBuffer);
      goto Xun;
    }
    Status = ShellGetFileSize (FileHandle, &Intermediate);

    Data = AllocateZeroPool ((UINTN)Intermediate);
    ShellReadFile (FileHandle, (UINTN *)&Intermediate, Data);

    CHAR8 filename8[128];


    int filename8_len = keynum;
    CHAR8 Intermediate_len[100];
    int_to_str(Intermediate,Intermediate_len);
    for (int i = 0; i < filename8_len; ++i) {
        filename8[i] = (CHAR8)FileNameBuffer[i];

    }
    Print(L"\n");

    filename8[filename8_len] = '\0';
    CHAR8 filenamelen[100];
    int_to_str(filename8_len,filenamelen);

    strcat(filename8, "|");
    strcat(filename8, Intermediate_len);
    strcat(filename8, "|");

    for (int i = 0; i < strlen(filename8); i++)
    {
      send(clnt_sock, &(filename8[i]), 1, 0);
      Print(L"%c ",filename8[i]);
    }

    send(clnt_sock, Data, (size_t)Intermediate, 0);
    Print(L"\nSend %s success\n",FileNameBuffer);
  }

Xun:
  Print(L"esc to quit server or anykey to continue..\r\n");
  gBS->WaitForEvent(1, &gST->ConIn->WaitForKey, &Index);
  gST->ConIn->ReadKeyStroke(gST->ConIn, &Key);
  if((Key.ScanCode == SCAN_ESC)){
    Print(L"Quit Server.\r\n"); break;
  }else
  {
    continue;
  }
}
End:
    close(clnt_sock);
    close(serv_sock);
    Print(L"Close Server.\r\n");
  return;
}

EFI_STATUS
EFIAPI
Server (
    IN EFI_HANDLE                     ImageHandle,
    IN EFI_SYSTEM_TABLE               *SystemTable )
{
    EFI_STATUS		Status = EFI_SUCCESS;
    EFI_SHELL_PARAMETERS_PROTOCOL     *pa = NULL;
    CHAR16                   *Operation;

    InitAmiLib(ImageHandle,SystemTable);

    Status = pBS->OpenProtocol(ImageHandle,
                                 &gEfiShellParametersProtocolGuid,
                                 (VOID **)&pa,
                                 ImageHandle,
                                 NULL,
                                 EFI_OPEN_PROTOCOL_GET_PROTOCOL
                                );
    if (EFI_ERROR (Status)) {
    Print(L"Couldn't open ShellInterface Protocol: %r\n", Status);
    return Status;
    }

    if (pa->Argc == 1)
    {
        Print(L"\n====================================================================\n");
        Print(L"Usage:\n");
        Print (L"    'Server.efi -s ' to start the server\n");
        Print (L"    'Server.efi -r xxx.efi' to run efi application\n");
        Print(L"====================================================================\n");
    }

    if (pa->Argc > 1) {
    Operation = (CHAR16*)pa->Argv[1];
    switch (Operation[1])
    {
      case L's':

        Print(L"\n");
        CreateServerApp();
        break;
      case L'r':
          // RunEfi(pa->Argv[2],ImageHandle);
          break;
      default:
          break;
      }
    }
    return Status;
}



