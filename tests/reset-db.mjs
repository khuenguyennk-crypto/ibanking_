import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const sql = readFileSync(new URL('./reset-data.sql', import.meta.url), 'utf8');

const result = spawnSync(
  'docker',
  ['compose', 'exec', '-T', 'db', 'sh', '-c', 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD"'],
  {input: sql, stdio: ['pipe', 'inherit', 'inherit']},
);

if (result.error) {
  console.error('Không chạy được docker:', result.error.message);
  process.exit(1);
}
if (result.status !== 0) process.exit(result.status);
console.log('Đã đưa dữ liệu về mẫu ban đầu.');
