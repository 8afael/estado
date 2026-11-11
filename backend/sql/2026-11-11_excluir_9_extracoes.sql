-- Remove 9 extrações que não fazem parte do corpus de 282 artigos
-- (base_geral_corrigida). artigo_id: 495, 97, 379, 77, 434, 332, 333, 492, 600
-- Faça backup do .db antes de rodar.
BEGIN;
DELETE FROM extracao_multivalores WHERE extracao_id IN (SELECT id FROM extracao_dados WHERE artigo_id IN (495,97,379,77,434,332,333,492,600));
DELETE FROM extracao_outros       WHERE extracao_id IN (SELECT id FROM extracao_dados WHERE artigo_id IN (495,97,379,77,434,332,333,492,600));
DELETE FROM extracao_dados        WHERE artigo_id IN (495,97,379,77,434,332,333,492,600);
COMMIT;
