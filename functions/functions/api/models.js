export async function onRequest(context) {
  const request = context.request;
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405, headers: corsHeaders });
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: '请求体不是有效 JSON' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  const baseUrl = String(body.baseUrl || '').trim().replace(/\/+$/, '');
  const apiKey = String(body.apiKey || '').trim();

  if (!baseUrl) {
    return new Response(JSON.stringify({ error: '缺少 baseUrl' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  const headers = {};
  if (apiKey) {
    headers['Authorization'] = 'Bearer ' + apiKey;
  }

  const url = baseUrl + '/models';
  const resp = await fetch(url, { method: 'GET', headers });
  const text = await resp.text();

  return new Response(text, {
    status: resp.status,
    headers: {
      ...corsHeaders,
      'Content-Type': resp.headers.get('Content-Type') || 'application/json',
    },
  });
}
