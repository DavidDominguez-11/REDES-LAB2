declare module "node:net" {
  interface Socket {
    on(event: string, listener: (...args: unknown[]) => void): Socket;
    write(data: Uint8Array): boolean;
    end(): void;
  }
  interface Server {
    listen(port: number, host: string, callback: () => void): Server;
    on(event: string, listener: (...args: unknown[]) => void): Server;
  }
  function createServer(listener: (socket: Socket) => void): Server;
  export { createServer, Socket };
}
declare const process: { argv: string[]; exitCode?: number };
