<?php
/**
 * @file
 * Página da Revista 2026: casca do desktop + coluna da edição, sem nenhum
 * invólucro em volta. O shell da #73 procura "body > main", então o <main>
 * do corpo precisa ser filho direto do <body>.
 *
 * Para quem pode editar, as abas (Ver/Editar) e as mensagens do Drupal ficam
 * numa caixa fixa no canto, fora do fluxo da página.
 */
?>
<?php if ($revista): ?>
<?php print $revista['corpo']; ?>

<?php if ($tabs = render($tabs)) $tabs = trim($tabs); ?>
<?php if ($messages || $tabs): ?>
<div class="revista2026-admin" style="position:fixed;right:12px;bottom:12px;z-index:2147483000;max-width:360px;padding:8px 12px;background:#fff;border:1px solid #999;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,.25);font:13px/1.4 Arial,sans-serif;color:#000;">
  <?php print $messages; ?>
  <?php print $tabs; ?>
</div>
<?php endif; ?>

<?php else: ?>
<?php /* fora de um conteúdo da revista (ThemeKey apontou outra página para este tema) */ ?>
<?php print $messages; ?>
<?php if ($tabs = render($tabs)) print $tabs; ?>
<?php print render($page['content']); ?>
<?php endif; ?>
