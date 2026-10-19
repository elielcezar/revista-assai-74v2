<?php
/**
 * @file
 * Configurações do tema Revista 2026 (Aparência > Configurações > Revista 2026).
 */

/**
 * Implements hook_form_FORM_ID_alter().
 */
function revista2026_form_system_theme_settings_alter(&$form, &$form_state) {
  $form['revista2026'] = array(
    '#type' => 'fieldset',
    '#title' => 'Revista 2026',
    '#weight' => -10,
  );
  $form['revista2026']['revista2026_tipo'] = array(
    '#type' => 'textfield',
    '#title' => 'Tipo de conteúdo',
    '#description' => 'Nome de máquina do tipo de conteúdo da revista. O tema só monta a página para esse tipo; vazio = qualquer conteúdo com corpo.',
    '#default_value' => theme_get_setting('revista2026_tipo'),
  );
  $form['revista2026']['revista2026_campo_css'] = array(
    '#type' => 'textfield',
    '#title' => 'Campo com os CSS da página',
    '#description' => 'Nome de máquina (ex.: field_css). Um endereço por item ou por linha; caminho relativo é lido a partir da pasta da edição no FTP.',
    '#default_value' => theme_get_setting('revista2026_campo_css'),
  );
  $form['revista2026']['revista2026_campo_js'] = array(
    '#type' => 'textfield',
    '#title' => 'Campo com os JS da página',
    '#description' => 'Nome de máquina (ex.: field_js). Mesmo formato do campo de CSS.',
    '#default_value' => theme_get_setting('revista2026_campo_js'),
  );
  $form['revista2026']['revista2026_gtm'] = array(
    '#type' => 'checkbox',
    '#title' => 'Inserir o Google Tag Manager da revista (GTM-MS6VK9B e GTM-W6GXJGP7)',
    '#description' => 'Desmarque se o site já insere o GTM por módulo, para não contar a visita duas vezes.',
    '#default_value' => theme_get_setting('revista2026_gtm'),
  );
}
