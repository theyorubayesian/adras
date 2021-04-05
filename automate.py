import datetime

import click
from crontab import CronTab
from crontab import CronItem


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)

    cron = CronTab(user=True)
    ctx.obj['cron'] = cron
    ctx.obj['default_command'] = 'python -m scripts.fullprocess'
    ctx.obj['default_comment'] = ''
    ctx.obj['default_refresh_minutes'] = 10


@cli.command()
@click.option('--command')
@click.option('--comment')
@click.option('--refresh_minutes', '-rm')
@click.pass_context
def add_cron_job(
        ctx,
        command,
        comment,
        refresh_minutes
) -> CronItem:
    cron = ctx.obj['cron']
    command = command or ctx.obj['default_command']
    comment = comment or ctx.obj['default_comment']
    refresh_minutes = refresh_minutes or ctx.obj['default_refresh_minutes']

    job = cron.new(command=command, comment=comment)
    job.minute.every(refresh_minutes)
    cron.write('cronjob')
    ctx.obj[f'job_{command}_{refresh_minutes}m'] = job
    print(job)
    return job


@cli.command()
@click.pass_context
def list_all_jobs(ctx):
    cron = ctx.obj['cron']
    for job in cron:
        print(job)


@cli.command()
@click.option('--command')
@click.pass_context
def delete_cron_job(ctx, command):
    cron = ctx.obj['cron']
    command = command or ctx.obj['default_command']
    try:
        job = next(cron.find_command(command))
        job.delete()
    except StopIteration:
        print(f'No job found with command: {command}')
        pass


@cli.command()
@click.option('--command')
@click.option('--comment')
@click.option('--refresh_minutes', '-rm')
@click.pass_context
def next_run_time(ctx, command, comment, refresh_minutes):
    cron = ctx.obj['cron']
    command = command or ctx.obj['default_command']
    for job in cron.find_command(command):
        schedule = job.schedule(date_from=datetime.datetime.now())
        print(schedule.get_next())


if __name__ == '__main__':
    cli()
