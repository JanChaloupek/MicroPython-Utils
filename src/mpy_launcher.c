#include <windows.h>
#include <wchar.h>

int wmain(int argc, wchar_t *argv[])
{
    wchar_t pythonCmd[4096] = L"python ";
    wchar_t scriptPath[MAX_PATH];

    // Získáme cestu k tomuto .exe
    GetModuleFileNameW(NULL, scriptPath, MAX_PATH);

    // Najdeme poslední lomítko a nahradíme název exe za "mpy"
    wchar_t *lastSlash = wcsrchr(scriptPath, L'\\');
    if (lastSlash) {
        wcscpy(lastSlash + 1, L"mpy");
    }

    // Sestavíme příkaz: python "cesta\mpy"
    wcscat(pythonCmd, L"\"");
    wcscat(pythonCmd, scriptPath);
    wcscat(pythonCmd, L"\"");

    // Přidáme argumenty
    for (int i = 1; i < argc; i++) {
        wcscat(pythonCmd, L" \"");
        wcscat(pythonCmd, argv[i]);
        wcscat(pythonCmd, L"\"");
    }

    // Spustíme Python jako nový proces
    STARTUPINFOW si = { sizeof(si) };
    PROCESS_INFORMATION pi;

    if (!CreateProcessW(NULL, pythonCmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)) {
        fwprintf(stderr, L"Chyba: nelze spustit Python.\n");
        return 1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    DWORD exitCode = 0;
    GetExitCodeProcess(pi.hProcess, &exitCode);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return exitCode;
}
