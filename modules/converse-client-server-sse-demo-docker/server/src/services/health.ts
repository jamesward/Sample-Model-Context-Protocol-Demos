import * as http from 'http';
import { env, APP_VERSION } from '../config/environment';

export const startHealthServer = (port: number = 8001): void => {
    const healthServer = http.createServer((req: http.IncomingMessage, res: http.ServerResponse) => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'healthy'
        }));
    });

    healthServer.listen(port, () => {
        console.log(`Health check server listening on port ${port}`);
    });
}; 