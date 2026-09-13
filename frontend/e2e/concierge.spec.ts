import { test, expect } from "@playwright/test";

test("objetivo conversacional sem diagnóstico, retomada e confirmação", async ({page,request}) => {
  const email = `concierge-${Date.now()}@example.com`;
  const password = "TestePrisma@2026";
  expect((await request.post("http://127.0.0.1:8002/auth/register",{data:{email,password}})).ok()).toBeTruthy();
  await page.goto("/login");
  await page.getByLabel("E-mail",{exact:true}).fill(email);
  await page.getByLabel("Senha",{exact:true}).fill(password);
  await page.getByRole("button",{name:"Entrar",exact:true}).click();
  await page.getByRole("button",{name:"Criar um objetivo",exact:true}).click();
  const send = async (text:string, expected:string) => {
    await page.getByLabel("Mensagem para o Prisma").fill(text);
    await page.getByRole("button",{name:"Enviar",exact:true}).click();
    await expect(page.getByText(expected,{exact:false}).last()).toBeVisible();
  };
  await send("Viagem em família","Quanto você pretende juntar");
  await send("12 mil","Daqui a quantos anos");
  await page.reload();
  await expect(page.getByText("Daqui a quantos anos",{exact:false})).toBeVisible();
  await send("2","Quanto já está guardado");
  await send("0","Quanto consegue guardar por mês");
  await send("500","Confira a proposta");
  await page.getByRole("button",{name:"Meu plano",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Viagem em família",exact:true})).toHaveCount(0);
  await page.getByRole("button",{name:"Conversa",exact:true}).click();
  await page.getByRole("button",{name:"Confirmar objetivo",exact:true}).click();
  await expect(page.getByText("Objetivo confirmado.",{exact:false})).toBeVisible();
  await page.getByRole("button",{name:"Meu plano",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Viagem em família",exact:true})).toBeVisible();
  await expect(page.getByText("Retorno nominal esperado (% a.a.)",{exact:true})).toBeHidden();
  await page.getByRole("button",{name:"Calcular cenário",exact:true}).click();
  await expect(page.getByText("Valor central projetado:",{exact:false})).toBeVisible();
  await page.getByRole("button",{name:"E se eu esperar mais um ano?",exact:true}).click();
  await expect(page.getByText("Valor central projetado:",{exact:false})).toHaveCount(2);
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({path:"test-results/prisma-plan-mobile.png",fullPage:true});
});
