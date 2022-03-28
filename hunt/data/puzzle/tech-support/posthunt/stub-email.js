const answers = [
    "AND",
    "ARM",
    "AZE",
    "BEL",
    "BRB",
    "FRA",
    "ITA", '840', 'UNITEDSTATESOFAMERICA', "USA", "US"
];

window.stubEmail = ({to, from, date, webpageUrl, chatUrl}) => {
  let at_part = to.match(/^.*\+(.*)@.+$/);
  at_part = at_part ? at_part[1].toUpperCase() : null;
  let replace = true

  const start_headers = {"x-message-query": "I'm a logical conjunction"}
  let email_headers = {}
  let subject = "Your Tech Support request"
  if (at_part && answers.includes(at_part)) {
      if (at_part === 'AND') // I
          email_headers = {
              'x-message-query': "Some alternative to x86/x64"
          }
      else if (at_part == "ARM") //S
          email_headers = {
              'x-message-query': "Often what you might see on a vehicle from Anhalt-Zerbst"
          }
      else if (at_part == "AZE") //O
          email_headers = {
              'x-message-query': "Say waist in Istanbul"
          }
      else if (at_part == "BEL") //S
          email_headers = {
              'x-message-query': "U no I'll return soon"
          }
      else if (at_part == "BRB") //U
          email_headers = {
              'x-message-query': "Major airport you might fly into if you want to see the Geographer in person"
          }
      else if (at_part == "FRA") //#M
          email_headers = {
              'x-message-query': "She's the chair of the ABC, down under"
          }
      else if (at_part == "ITA") //S
          email_headers['x-message'] = "Please request again with your email alias + ans"
      else if (at_part == "840") {
          subject = "🤏 " + subject
          email_headers['x-message'] = "This is a clue for the answer you want, in short."
          replace = false;
      } else if (at_part == "UNITEDSTATESOFAMERICA") {
          subject = "🤏 " + subject
          email_headers['x-message'] = "This is the country you want, briefly."
          replace = false;
      } else if (at_part == "US") {
          subject = "🤏 " + subject
          email_headers['x-message'] = "This is not the ans we are looking for."
          replace = false;
      } else if (at_part == "USA") {
          subject = "🇺🇸 " + subject
          email_headers['x-message'] = "Thank you. For further assistance, please seek support via chat or webpage."
          replace = false;
      } else
          email_headers = start_headers
  } else {
          if (to.indexOf('+'))
              subject = "⛔ " + subject;
          email_headers = start_headers
  }

  if (replace)
      email_headers['x-message'] = "Please request again with your email alias + ans";

  const email_headers_str = Object.entries(email_headers).map(([k, v]) => `${k}: ${v}`).join('\n');
  const downloadStr = `Delivered-To: ${to}
Received: by 2001:ac4:9923:0:c0:4ab:d95d:2745 with SMTP id c41csp1307277pit;
        ${date}
Return-Path: <bounce+faf818.0b0fc9-${to.replace('@', '=')}@mg.mitmh2022.com>
Received: from m43-13.mailgun.net (m43-13.mailgun.net. [91.121.2.91])
        by mx.google.com with UTF8SMTPS id s124-20020a819b82000000b002e5cd04a5b1si1089542ywg.279.2021.14.24.16.49.43
        for <${to}>
        (version=TLS1_3 cipher=TLS_AES_128_GCM_SHA256 bits=128/128);
        ${date}
Received-SPF: pass (google.com: domain of bounce+faf818.0a0fc4-${to.replace('@', '=')}@mg.mitmh2022.com designates 91.121.2.91 as permitted sender) client-ip=91.121.2.91;
Authentication-Results: mx.google.com;
       dkim=pass header.i=@mg.mitmh2022.com header.s=mailo header.b=ppDEhCd2;
       dkim=pass header.i=@mailgun.org header.s=mg2 header.b=Fb2KhyIB;
       spf=pass (google.com: domain of bounce+faf818.0a0fc4-${to.replace('@', '=')}@mg.mitmh2022.com designates 91.121.2.91 as permitted sender) smtp.mailfrom="bounce+faf818.0a0fc4-${to.replace('@', '=')}@mg.mitmh2022.com"
DKIM-Signature: a=rsa-sha256; v=1; c=relaxed/relaxed; d=mg.mitmh2022.com; q=dns/txt; s=mailo; t=1648165790; h=Message-Id: Reply-To: To: To: From: From: Subject: Subject: Content-Type: Mime-Version: Date: Sender: Sender: X-Feedback-Id; bh=ym/8BYJVNFkCm6fI/ghUwJDeDq+p1i8kF/uC+hFrkZw=; b=ppDNhZd2F4ln5mwmcberCDq4+fCNa0XKaHUuyjUvuy1SS9pXM3WxAW/6ew7iK4Q5PdymK/kt IFbVqIFfUByu0E/3BLd5HlZdGg7ljNP4UUW6ZKK2RZiIeNXKWJygeDhiM7v6eLeKFsGY5i5p tkyh07q6EWD65++pDCRYyPvK2W0=
DKIM-Signature: a=rsa-sha256; v=1; c=relaxed/relaxed; d=mailgun.org; q=dns/txt; s=mg2; t=1648165790; h=Message-Id: Reply-To: To: To: From: From: Subject: Subject: Content-Type: Mime-Version: Date: Sender: Sender: X-Feedback-Id; bh=ym/8BYJVNFkCm6fI/ghUwJDeDq+p1i8kF/uC+hFrkZw=; b=Fb2KhyIA8aUzOV4Xjy/+XtvUrBaOSWWHAuCzQP/BWVoU91AnQMc4VmS85qsnaGbC7ohS5Czr EZPuwbSAk/d/2IOiq5wyMerOL2oQ5sY99zc7z+Ty+8d7EelubW4j2KNGBgOPOUJqoJWJc4lP jGvpJ0fxQLxtFNW1CBzza2oECeU=
X-Feedback-Id: 61b5a15a6b53c2b984f29cc4:mailgun
X-Mailgun-Sending-Ip: 91.121.2.91
X-Mailgun-Sid: WyIzMDUxNSIsICJzYjM3MDArYW5kQGdtYWlsLmNvbSIsICIwYTBmYzQiXQ==
Received: from <unknown> (<unknown> []) by api-n14.prod.us-west-2.postgun.com with HTTP id 623d0383ab3ee5b49f9664cd; ${date}
Sender: ${from.replace('@', '=')}@mg.mitmh2022.com
Date: ${date}
Mime-Version: 1.0
Content-Type: multipart/alternative; boundary=bd3d444de43f9f823e1cd9775758e3c9ac9072270d30ddfaceae6aaf6835
Subject: ${subject}
From: ${from}
To: ${to}
Reply-To: ${from}
${email_headers_str}
Message-Id: <20220324234923.043040b00d6178ba@mg.mitmh2022.com>

--bd3d444de43f9f823e1cd9775758e3c9ac9072270d30ddfaceae6aaf6835
Content-Transfer-Encoding: quoted-printable
Content-Type: text/plain; charset="utf-8"

Hi,

Emails can contain useful information.

After reading it initially, you should probably look in the places indicate=
d.

Don=E2=80=99t forget to inspect HTTP responses for them!

Even if you don=E2=80=99t get the whole answer at first, remember that we h=
ave [webpage](webpageUrl), email, and=
 [chat support](chatUrl).

Reach out to us on all our support channels - they don=E2=80=99t connect we=
ll to start with, but they come together in the end.

Sincerely, New You City Tech Support
--bd3d444de43f9f823e1cd9775758e3c9ac9072270d30ddfaceae6aaf6835
Content-Transfer-Encoding: quoted-printable
Content-Type: text/html; charset="utf-8"

<p>Hi,</p>

<p>Emails can contain useful information.</p>

<p>After reading it initially, you should probably look in the places indic=
ated.</p>

<p>Don=E2=80=99t forget to inspect HTTP responses for them!</p>

<p>Even if you don=E2=80=99t get the whole answer at first, remember that w=
e have <a href=3D"webpageUrl">webpage=
</a>, email, and <a href=3D"chatUrl">chat support</a>.</p>

<p>Reach out to us on all our support channels - they don=E2=80=99t connect=
 well to start with, but they come together in the end.</p>

<p>Sincerely, New You City Tech Support</p>

--bd3d444de43f9f823e1cd9775758e3c9ac9072270d30ddfaceae6aaf6835--`;

  const downloadBlob = new Blob([downloadStr], {type: 'text/plain'});
  return {subject, downloadBlob};
}
