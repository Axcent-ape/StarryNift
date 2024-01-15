from datetime import timedelta
from data import config
from core.starry_nift import StarryNift
from core.utils import random_line, logger
import asyncio


async def start(thread):
    logger.info(f"Поток {thread} | Начал работу")
    while True:
        private_key = await random_line('data/private_keys.txt')
        if not private_key: break

        starry = StarryNift(key=private_key, referral_link=config.REF_LINK, bnb_rpc=config.BNB_RPC)
        if await starry.login():
            if not await starry.check_minted_pass():
                await starry.mint_pass(logger=logger, thread=thread, gas_price=config.MINT_GWEI)

            time_to_claim = await starry.get_daily_claim_time()
            if time_to_claim == 0:
                await starry.daily_claim(logger, thread, config.MINT_GWEI)
            else: logger.warning(f"Поток {thread} | Следующий клейм через {str(timedelta(seconds=time_to_claim))}: {starry.web3_utils.acct.address}")

        await starry.logout()
    logger.info(f"Поток {thread} | Закончил работу")


async def main():
    print("Автор софта: https://t.me/ApeCryptor")

    thread_count = int(input("Введите кол-во потоков: "))
    # thread_count = 1
    tasks = []
    for thread in range(1, thread_count+1):
        tasks.append(asyncio.create_task(start(thread)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

