import { TcbEventFunction } from '@cloudbase/functions-typings';
import { StreamableHTTPMCPServerRunner } from '@cloudbase/mcp/cloudrun';
import { createServer } from './server.js';

export const main: TcbEventFunction<unknown> = async function (event, context) {
  const runner = new StreamableHTTPMCPServerRunner(createServer, {
    verifyAccess: process.env.SKIP_VERIFY_ACCESS === 'true' ? false : true,
  });
  return runner.run(event, context);
};
