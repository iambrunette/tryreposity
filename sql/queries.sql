-- Найти все переводы за последние 24 часа
SELECT * FROM transfers_transfer
WHERE created_at >= datetime('now', '-1 day');

-- Найти сумму всех завершённых переводов
SELECT SUM(amount) AS total_completed
FROM transfers_transfer
WHERE status = 'completed';

-- Найти переводы по конкретному отправителю
SELECT * FROM transfers_transfer
WHERE sender_card_number = '1234 5678 9012 3456';
